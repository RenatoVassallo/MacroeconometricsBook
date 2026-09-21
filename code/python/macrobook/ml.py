"""Machine learning for macro forecasting: FRED-MD, features, backtest.

The chapter on machine learning (chapter 11) uses four pieces:

* `load_fredmd` reads the frozen FRED-MD vintage and applies the
  McCracken-Ng transformation codes.
* `feature_matrix` stacks the transformed panel and its lags, so the row
  dated t contains only values dated t or earlier (publication lags and
  data revisions are ignored: this is a pseudo real-time design).
* `backtest` re-estimates every model once a year on an expanding window
  and forecasts each month with the latest estimates.
* `permutation_importance` measures how much a fitted model leans on a
  group of predictors outside the estimation sample.

Everything that learns from the data (scaling, principal components,
penalties, trees) is fitted inside the estimation window of each origin.
"""

from __future__ import annotations

import re

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.compose import ColumnTransformer
from sklearn.decomposition import PCA
from sklearn.ensemble import (HistGradientBoostingRegressor,
                              RandomForestRegressor)
from sklearn.linear_model import Lasso, LinearRegression, Ridge
from sklearn.model_selection import GridSearchCV, TimeSeriesSplit
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

# The eight groups of McCracken and Ng (2016), by mnemonic.
GROUPS = [
    ("producción e ingreso", r"^(RPI|W875RX1|INDPRO|IP|CUMFNS)"),
    ("mercado laboral",
     r"^(HWI|CLF16OV|CE16OV|UNRATE|UEMP|CLAIMS|PAYEMS|USGOOD|CES"
     r"|USCONS|MANEMP|DMANEMP|NDMANEMP|SRVPRD|USTPU|USWTRADE"
     r"|USTRADE|USFIRE|USGOVT|AWOTMAN|AWHMAN)"),
    ("vivienda", r"^(HOUST|PERMIT)"),
    ("consumo, órdenes e inventarios",
     r"^(DPCERA3M086SBEA|CMRMTSPL|RETAIL|ACOGNO|AMDMNO|ANDENO"
     r"|AMDMUO|BUSINV|ISRATIO|UMCSENT)"),
    ("dinero y crédito",
     r"^(M1SL|M2SL|M2REAL|BOGMBASE|TOTRESNS|NONBORRES|BUSLOANS"
     r"|REALLN|NONREVSL|CONSPI|DTCOLNVHFNM|DTCTHFNM|INVEST)"),
    ("tasas y tipos de cambio",
     r"^(FEDFUNDS|CP3M|TB3MS|TB6MS|GS1|GS5|GS10|AAA|BAA|COMPAPFF"
     r"|TB3SMFFM|TB6SMFFM|T1YFFM|T5YFFM|T10YFFM|TWEX|EX)"),
    ("precios",
     r"^(WPS|OILPRICE|PPICMM|CPI|CUSR|PCEPI|DDURRG|DNDGRG|DSERRG)"),
    ("mercado bursátil", r"^(S&P|VIX)"),
]


def group_of(series: str) -> str:
    """FRED-MD group of a series; own inflation lags are their own."""
    if series == "INFL":
        return "inflación rezagada"
    for name, pattern in GROUPS:
        if re.match(pattern, series):
            return name
    raise KeyError(f"{series} has no FRED-MD group")


def apply_tcode(x: pd.Series, code: int) -> pd.Series:
    """McCracken-Ng transformation codes 1-7."""
    if code == 1:
        return x
    if code == 2:
        return x.diff()
    if code == 3:
        return x.diff().diff()
    logx = np.log(x.where(x > 0))
    if code == 4:
        return logx
    if code == 5:
        return logx.diff()
    if code == 6:
        return logx.diff().diff()
    if code == 7:
        return (x / x.shift(1) - 1.0).diff()
    raise ValueError(f"unknown transformation code {code}")


def load_fredmd(path) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame]:
    """Return (raw, tcodes, transformed) with a monthly PeriodIndex."""
    table = pd.read_csv(path)
    tcodes = table.iloc[0, 1:].astype(float).astype(int)
    raw = table.iloc[1:].copy()
    dates = pd.to_datetime(raw.iloc[:, 0], format="%m/%d/%Y")
    raw.index = pd.PeriodIndex(dates, freq="M")
    raw = raw.iloc[:, 1:].astype(float)
    transformed = pd.DataFrame({c: apply_tcode(raw[c], tcodes[c])
                                for c in raw.columns})
    return raw, tcodes, transformed


def target(inflation: pd.Series, h: int) -> pd.Series:
    """Average annualised inflation over months t+1..t+h, dated t."""
    ahead = sum(inflation.shift(-j) for j in range(1, h + 1)) / h
    return ahead.rename(f"target_h{h}")


def feature_matrix(panel: pd.DataFrame, inflation: pd.Series,
                   lags: int = 4) -> pd.DataFrame:
    """Transformed series and inflation at t, t-1, ..., t-lags+1."""
    blocks = {f"{c}_l{lag}": panel[c].shift(lag)
              for c in panel.columns for lag in range(lags)}
    for lag in range(lags):
        blocks[f"INFL_l{lag}"] = inflation.shift(lag)
    return pd.DataFrame(blocks)


def dm_test(e_model, e_bench, h: int = 1):
    """Diebold-Mariano test of equal squared error (Newey-West, HLN).

    Negative statistics favour the model. With nested models (every
    model here nests the AR benchmark) the test is conservative.
    """
    d = np.asarray(e_model) ** 2 - np.asarray(e_bench) ** 2
    n = len(d)
    dc = d - d.mean()
    lags = max(h - 1, int(np.floor(4 * (n / 100) ** (2 / 9))))
    lrv = dc @ dc / n
    for k in range(1, lags + 1):
        weight = 1 - k / (lags + 1)
        lrv += 2 * weight * (dc[k:] @ dc[:-k]) / n
    stat = d.mean() / np.sqrt(lrv / n)
    stat *= np.sqrt((n + 1 - 2 * h + h * (h - 1) / n) / n)
    return stat, 2 * stats.t.sf(abs(stat), df=n - 1)


def models(ar_cols, panel_cols, alpha_ridge, alpha_lasso, seed=0):
    """The six forecasting models of chapter 11, as sklearn objects."""
    ar = ColumnTransformer([("ar", "passthrough", ar_cols)])
    factors = ColumnTransformer([
        ("ar", "passthrough", ar_cols),
        ("pc", make_pipeline(StandardScaler(), PCA(4)), panel_cols)])
    return {
        "AR": make_pipeline(ar, LinearRegression()),
        "factores": make_pipeline(factors, LinearRegression()),
        "ridge": make_pipeline(StandardScaler(), Ridge(alpha_ridge)),
        "lasso": make_pipeline(StandardScaler(),
                               Lasso(alpha_lasso, max_iter=20_000)),
        "bosque": RandomForestRegressor(
            300, max_features=1 / 3, min_samples_leaf=5,
            n_jobs=-1, random_state=seed),
        "boosting": HistGradientBoostingRegressor(
            learning_rate=0.05, max_iter=300, max_depth=3,
            l2_regularization=1.0, early_stopping=False,
            random_state=seed),
    }


def tune(estimator, grid, X, y, h):
    """Grid search with time-ordered folds and an h-1 gap."""
    cv = TimeSeriesSplit(n_splits=5, test_size=24, gap=h - 1)
    search = GridSearchCV(estimator, grid, cv=cv,
                          scoring="neg_root_mean_squared_error")
    search.fit(X, y)
    return search.best_params_, -search.best_score_


def backtest(models: dict, X: pd.DataFrame, y: pd.Series,
             first: str, last: str, h: int,
             refit_month: int = 12) -> pd.DataFrame:
    """Expanding-window pseudo out-of-sample forecasts.

    For every origin t between `first` and `last`, the models are
    trained on the rows whose target is already observed at t (target
    date t' + h <= t) and forecast y[t]. They are re-estimated only in
    the month `refit_month` of each year and at the first origin.
    """
    data = pd.concat([X, y.rename("y")], axis=1).dropna(
        subset=list(X.columns))
    origins = data.loc[first:last].index
    rows, fitted = [], {}
    for t in origins:
        if not fitted or t.month == refit_month:
            known = data.loc[: t - h].dropna(subset=["y"])
            for name, model in models.items():
                fitted[name] = model.fit(known[X.columns], known["y"])
        x_t = data.loc[[t], X.columns]
        for name, model in fitted.items():
            rows.append({"origin": t, "model": name, "h": h,
                         "forecast": float(model.predict(x_t)[0]),
                         "actual": data.loc[t, "y"]})
    return pd.DataFrame(rows)


def permutation_importance(model, X: pd.DataFrame, y: pd.Series,
                           groups: dict, repeats: int = 20,
                           seed: int = 0) -> pd.DataFrame:
    """Increase in RMSE when each group of columns is shuffled.

    `groups` maps a name to a list of columns. All columns of a group
    are permuted with the same row order, so a series and its lags,
    or a block of close substitutes, lose their information together.
    Returns the mean and the standard deviation over `repeats`; the
    RMSE without shuffling is stored in `table.attrs["base"]`.
    """
    rng = np.random.default_rng(seed)

    def rmse(frame):
        return np.sqrt(np.mean((y - model.predict(frame)) ** 2))

    base = rmse(X)
    rows = {}
    for name, cols in groups.items():
        losses = []
        for _ in range(repeats):
            shuffled = X.copy()
            order = rng.permutation(len(X))
            shuffled[cols] = X[cols].to_numpy()[order]
            losses.append(rmse(shuffled) - base)
        rows[name] = {"mean": np.mean(losses), "sd": np.std(losses)}
    table = pd.DataFrame(rows).T.sort_values("mean")
    table.attrs["base"] = base
    return table
