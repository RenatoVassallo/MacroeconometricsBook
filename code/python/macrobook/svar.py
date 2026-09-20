"""Structural VAR: identification, responses, variance and history.

Conventions extend those of `var.py`:

    y_t = c + Phi_1 y_{t-1} + ... + Phi_p y_{t-p} + u_t,
    u_t = S eps_t,  eps_t ~ N(0, I_n),  Sigma = E[u_t u_t'] = S S'.

`S` is the impact matrix (n, n): column k holds the impact of structural shock
k on every variable. Structural responses come as an array of shape
(h + 1, n, n) whose entry [j, i, k] is the response of variable i to shock k at
horizon j, that is Theta_j = Psi_j S with Psi_j the Wold weights of `var.py`.
"""

from __future__ import annotations

from typing import Callable

import numpy as np

from .var import coefficients_by_lag, ma_weights, ols

Identifier = Callable[[np.ndarray, np.ndarray, int, int], np.ndarray]
"""Signature of an identification scheme: (Sigma, B, n, p) -> S."""


# ------------------------------------------------------------ identification
def normalize_signs(S: np.ndarray) -> np.ndarray:
    """Flip columns so that every shock raises its own variable on impact."""
    S = np.asarray(S, dtype=float).copy()
    flip = np.where(np.diag(S) < 0, -1.0, 1.0)
    return S * flip


def cholesky_impact(Sigma, B=None, n=None, p=None) -> np.ndarray:
    """Lower-triangular S with S S' = Sigma (recursive identification).

    The unused arguments keep the signature of an identification scheme, so
    the function can be passed to `bootstrap_bands`.
    """
    return np.linalg.cholesky(np.asarray(Sigma, dtype=float))


def long_run_impact(Sigma: np.ndarray, B: np.ndarray, n: int, p: int) -> np.ndarray:
    """Impact matrix with a lower-triangular long-run effect (Blanchard-Quah).

    The cumulative effect of the shocks is A^{-1} S with A = I - Phi_1 - ...
    - Phi_p. Imposing that A^{-1} S be lower triangular gives
    S = A chol(A^{-1} Sigma A^{-1}').
    """
    phis, _ = coefficients_by_lag(B, n, p)
    A = np.eye(n) - sum(phis)
    A_inv = np.linalg.inv(A)
    Omega = A_inv @ np.asarray(Sigma, dtype=float) @ A_inv.T
    return normalize_signs(A @ np.linalg.cholesky(Omega))


def random_orthonormal(n: int, rng: np.random.Generator) -> np.ndarray:
    """Draw Q with Q Q' = I from the Haar measure on the orthogonal group."""
    Q, R = np.linalg.qr(rng.standard_normal((n, n)))
    return Q * np.sign(np.diag(R))


def _flips(theta_by_horizon, signs: np.ndarray):
    """Column signs that make every restricted response match, or None.

    A shock and its negative are the same shock with the opposite name, so each
    column may be multiplied by -1, but by the same factor at every horizon.
    """
    n = signs.shape[1]
    flips = np.ones(n)
    for k in range(n):
        wanted = signs[:, k]
        rows = wanted != 0
        if not np.any(rows):
            continue
        for flip in (1.0, -1.0):
            if all(np.all(np.sign(flip * theta[rows, k]) == wanted[rows])
                   for theta in theta_by_horizon):
                flips[k] = flip
                break
        else:
            return None
    return flips


def sign_restricted_impacts(Sigma: np.ndarray, B: np.ndarray, n: int, p: int,
                            signs: np.ndarray, horizons=(0,),
                            draws: int = 500, max_tries: int = 200_000,
                            seed: int | None = None) -> np.ndarray:
    """Accept-reject sampler of impact matrices consistent with `signs`.

    `signs` is an (n, n) array of +1, -1 and 0, where 0 leaves the entry free
    and column k describes shock k. The pattern is checked on the responses at
    every horizon in `horizons`. Returns an array (accepted, n, n): every S in
    it satisfies S S' = Sigma and the sign pattern.
    """
    rng = np.random.default_rng(seed)
    P = np.linalg.cholesky(np.asarray(Sigma, dtype=float))
    signs = np.asarray(signs)
    psis = ma_weights(B, n, p, max(horizons))
    accepted, tries = [], 0
    while len(accepted) < draws and tries < max_tries:
        tries += 1
        candidate = P @ random_orthonormal(n, rng)
        theta_by_horizon = [psis[j] @ candidate for j in horizons]
        flips = _flips(theta_by_horizon, signs)
        if flips is not None:
            accepted.append(candidate * flips)
    return np.array(accepted)


# ----------------------------------------------------------------- responses
def responses(B: np.ndarray, S: np.ndarray, n: int, p: int, h: int) -> np.ndarray:
    """Theta_j = Psi_j S for j = 0, ..., h; shape (h + 1, n, n)."""
    return ma_weights(B, n, p, h) @ np.asarray(S, dtype=float)


def structural_shocks(residuals: np.ndarray, S: np.ndarray) -> np.ndarray:
    """eps_t = S^{-1} u_t, shape (T, n)."""
    return np.linalg.solve(np.asarray(S, dtype=float),
                           np.asarray(residuals, dtype=float).T).T


def fevd(B: np.ndarray, S: np.ndarray, n: int, p: int, h: int) -> np.ndarray:
    """Share of the forecast error variance by horizon, shape (h + 1, n, n)."""
    contributions = np.cumsum(responses(B, S, n, p, h) ** 2, axis=0)
    return contributions / contributions.sum(axis=2, keepdims=True)


def historical_decomposition(y: np.ndarray, B: np.ndarray, S: np.ndarray,
                             n: int, p: int):
    """Contribution of every shock to every variable, period by period.

    Returns (contributions, baseline) with shapes (T - p, n, n) and (T - p, n):
    y[p:] equals baseline plus the sum of the contributions over shocks.
    """
    fit = ols(np.asarray(y, dtype=float), p)
    eps = structural_shocks(fit["residuals"], S)
    T_eff = eps.shape[0]
    theta = responses(B, S, n, p, T_eff - 1)
    contributions = np.zeros((T_eff, n, n))
    for t in range(T_eff):
        for lag in range(t + 1):
            contributions[t] += theta[lag] * eps[t - lag]
    baseline = fit["Y"] - contributions.sum(axis=2)
    return contributions, baseline


# ----------------------------------------------------------------- inference
def unit_scale(S: np.ndarray) -> np.ndarray:
    """Rescale every column so the shock moves its own variable by one unit."""
    S = np.asarray(S, dtype=float)
    return S / np.diag(S)


def bootstrap_bands(y: np.ndarray, p: int, h: int,
                    identify: Identifier = cholesky_impact,
                    draws: int = 1000, level: float = 0.95,
                    cumulate: bool = False, unit: bool = False,
                    seed: int | None = None):
    """Percentile bootstrap bands for the structural responses.

    Recursive design: residuals are resampled with replacement, the sample is
    rebuilt with the estimated coefficients, and the whole procedure
    (estimation and identification) is repeated on each artificial sample.
    Returns (lower, upper), both of shape (h + 1, n, n).
    """
    y = np.asarray(y, dtype=float)
    T, n = y.shape
    fit = ols(y, p)
    phis, c = coefficients_by_lag(fit["B"], n, p)
    U = fit["residuals"]
    rng = np.random.default_rng(seed)
    store = np.empty((draws, h + 1, n, n))
    for b in range(draws):
        U_star = U[rng.integers(0, U.shape[0], U.shape[0])]
        y_star = np.empty((T, n))
        y_star[:p] = y[:p]
        for t in range(p, T):
            value = c + U_star[t - p]
            for lag, Phi in enumerate(phis, start=1):
                value = value + Phi @ y_star[t - lag]
            y_star[t] = value
        fit_b = ols(y_star, p)
        S_b = normalize_signs(identify(fit_b["Sigma"], fit_b["B"], n, p))
        if unit:
            S_b = unit_scale(S_b)
        theta = responses(fit_b["B"], S_b, n, p, h)
        store[b] = np.cumsum(theta, axis=0) if cumulate else theta
    tail = (1 - level) / 2
    return np.quantile(store, tail, axis=0), np.quantile(store, 1 - tail, axis=0)


# ------------------------------------------------------- local projections
def local_projection(y: np.ndarray, shock: np.ndarray, horizon: int,
                     lags: int = 2, level: float = 0.95):
    """Response at `horizon` estimated equation by equation (Jorda, 2005).

    `shock` is aligned with the rows of `y` and may start with NaN (the first
    observations, for which the VAR has no residual). Each regression puts
    y_{i,t+h} on the shock and on `lags` lags of every variable; standard
    errors are Newey-West with horizon + 1 lags. Returns (point, lower, upper),
    each of length n.
    """
    y = np.asarray(y, dtype=float)
    shock = np.asarray(shock, dtype=float)
    T, n = y.shape
    rows = np.arange(lags, T - horizon)
    rows = rows[~np.isnan(shock[rows])]
    controls = [y[rows - lag] for lag in range(1, lags + 1)]
    X = np.column_stack([np.ones(len(rows)), shock[rows]] + controls)
    point, se = np.empty(n), np.empty(n)
    for i in range(n):
        target = y[rows + horizon, i]
        beta, *_ = np.linalg.lstsq(X, target, rcond=None)
        residual = target - X @ beta
        XtX_inv = np.linalg.inv(X.T @ X)
        variance = XtX_inv @ _newey_west(X, residual, horizon + 1) @ XtX_inv
        point[i], se[i] = beta[1], np.sqrt(variance[1, 1])
    z = _normal_quantile(level)
    return point, point - z * se, point + z * se


def _newey_west(X: np.ndarray, residual: np.ndarray, lags: int) -> np.ndarray:
    T = X.shape[0]
    S = (X * residual[:, None]).T @ (X * residual[:, None])
    for lag in range(1, lags + 1):
        weight = 1.0 - lag / (lags + 1.0)
        left = (X[lag:] * residual[lag:, None]).T @ (X[:-lag] * residual[:-lag, None])
        S = S + weight * (left + left.T)
    return S


def _normal_quantile(level: float) -> float:
    from statistics import NormalDist

    return NormalDist().inv_cdf(0.5 + level / 2)
