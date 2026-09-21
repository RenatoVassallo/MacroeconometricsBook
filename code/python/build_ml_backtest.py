"""Pseudo out-of-sample backtest of chapter 11 (FRED-MD, US inflation).

Forecasts average CPI inflation over the next h months (h = 1 and 12)
with an AR benchmark, factors, ridge, lasso, a random forest and
gradient boosting. Penalties are chosen once, on the development sample
(targets observed by 1989-12), with time-ordered validation; every model
is then re-estimated each December on an expanding window.

    uv run python code/python/build_ml_backtest.py   (about 10 minutes)

Writes data/processed/ml_backtest.csv and ml_hyperparameters.csv.
"""

from __future__ import annotations

import time

import numpy as np
import pandas as pd
from sklearn.linear_model import Lasso, Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from macrobook import data_path
from macrobook.ml import backtest, feature_matrix, models, target, tune

HORIZONS = (1, 12)
DEV_END = "1989-12"            # last origin whose target is fully known
TEST = ("1990-01", "2025-08")  # origins; targets end in 2025-09


if __name__ == "__main__":
    panel = pd.read_csv(data_path("fredmd_panel.csv"), index_col="date")
    panel.index = pd.PeriodIndex(panel.index, freq="M")
    inflation = panel.pop("INFL")
    X = feature_matrix(panel, inflation).dropna()
    ar_cols = [c for c in X.columns if c.startswith("INFL_")]
    panel_cols = [f"{c}_l0" for c in panel.columns]

    results, chosen = [], []
    for h in HORIZONS:
        y = target(inflation, h)
        dev = pd.concat([X, y], axis=1).loc[:DEV_END].dropna()
        Xd, yd = dev[X.columns], dev[y.name]
        ridge, rmse_r = tune(make_pipeline(StandardScaler(), Ridge()),
                             {"ridge__alpha": np.logspace(0, 6, 25)},
                             Xd, yd, h)
        lasso, rmse_l = tune(
            make_pipeline(StandardScaler(), Lasso(max_iter=20_000)),
            {"lasso__alpha": np.logspace(-3, 1, 25)}, Xd, yd, h)
        alpha_r, alpha_l = ridge["ridge__alpha"], lasso["lasso__alpha"]
        dev_lasso = make_pipeline(StandardScaler(),
                                  Lasso(alpha_l, max_iter=20_000))
        coef = pd.Series(dev_lasso.fit(Xd, yd)[-1].coef_, index=X.columns)
        kept = coef[coef != 0].abs().sort_values(ascending=False)
        chosen.append({"h": h, "ridge_alpha": alpha_r,
                       "ridge_rmse": rmse_r, "lasso_alpha": alpha_l,
                       "lasso_rmse": rmse_l, "lasso_kept": len(kept),
                       "lasso_top": " ".join(kept.index[:6])})
        print(f"h={h}: ridge alpha {alpha_r:.3g}, "
              f"lasso alpha {alpha_l:.3g}")

        start = time.time()
        specs = models(ar_cols, panel_cols, alpha_r, alpha_l)
        out = backtest(specs, X, y, *TEST, h=h)
        # Atkeson-Ohanian benchmark: inflation of the last 12 months
        last12 = inflation.rolling(12).mean()
        bench = out[out.model == "AR"].copy()
        bench["model"] = "promedio 12m"
        bench["forecast"] = last12.reindex(bench["origin"]).to_numpy()
        results += [out, bench]
        print(f"h={h}: {time.time() - start:.0f} s")

    table = pd.concat(results, ignore_index=True)
    table.to_csv(data_path("ml_backtest.csv"), index=False)
    pd.DataFrame(chosen).to_csv(data_path("ml_hyperparameters.csv"),
                                index=False)
    print(table.groupby(["h", "model"]).size())
