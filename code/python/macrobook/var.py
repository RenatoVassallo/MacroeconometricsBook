"""Classical VAR: matrices, OLS, companion form and forecasting.

Book conventions:

    y_t = c + Phi_1 y_{t-1} + ... + Phi_p y_{t-p} + u_t,   u_t ~ N(0, Sigma)

with `y` of shape (T, n) and `B` of shape (k, n), k = n*p + 1, the CONSTANT IN
THE FIRST ROW, followed by the lags. The companion matrix F is (n*p, n*p).

Note: MacroPy stacks the constant last. When comparing coefficient vectors with
MacroPy, reorder first.
"""

from __future__ import annotations

import numpy as np


def lag_matrix(y: np.ndarray, p: int, constant: bool = True):
    """Return (Y, X) with Y = y[p:] and X = [1, y_{t-1}, ..., y_{t-p}]."""
    y = np.asarray(y, dtype=float)
    T, n = y.shape
    columns = [y[p - lag : T - lag] for lag in range(1, p + 1)]
    X = np.column_stack(columns)
    if constant:
        X = np.column_stack([np.ones(T - p), X])
    return y[p:], X


def ols(y: np.ndarray, p: int, constant: bool = True) -> dict:
    """Equation-by-equation OLS (same as GLS and as conditional ML)."""
    Y, X = lag_matrix(y, p, constant)
    B = np.linalg.solve(X.T @ X, X.T @ Y)
    U = Y - X @ B
    T_eff, k = X.shape
    Sigma = U.T @ U / (T_eff - k)
    return {"B": B, "Sigma": Sigma, "residuals": U, "Y": Y, "X": X,
            "p": p, "constant": constant, "T": T_eff, "k": k}


def coefficients_by_lag(B: np.ndarray, n: int, p: int):
    """Split B into (Phi_1, ..., Phi_p) and the constant vector c."""
    B = np.asarray(B, dtype=float)
    has_constant = B.shape[0] == n * p + 1
    offset = 1 if has_constant else 0
    phis = [B[offset + (lag - 1) * n : offset + lag * n, :].T for lag in range(1, p + 1)]
    c = B[0, :] if has_constant else np.zeros(n)
    return phis, c


def companion(B: np.ndarray, n: int, p: int) -> np.ndarray:
    """Companion matrix F (n*p x n*p) of the VAR(p)."""
    phis, _ = coefficients_by_lag(B, n, p)
    F = np.zeros((n * p, n * p))
    F[:n] = np.hstack(phis)
    if p > 1:
        F[n:, : n * (p - 1)] = np.eye(n * (p - 1))
    return F


def roots(B: np.ndarray, n: int, p: int) -> np.ndarray:
    """Eigenvalues of the companion matrix, sorted by decreasing modulus."""
    lam = np.linalg.eigvals(companion(B, n, p))
    return lam[np.argsort(-np.abs(lam))]


def is_stable(B: np.ndarray, n: int, p: int, tolerance: float = 1.0) -> bool:
    return bool(np.max(np.abs(roots(B, n, p))) < tolerance)


def unconditional_mean(B: np.ndarray, n: int, p: int) -> np.ndarray:
    """mu = (I - Phi_1 - ... - Phi_p)^{-1} c. Only meaningful if the VAR is stable."""
    phis, c = coefficients_by_lag(B, n, p)
    return np.linalg.solve(np.eye(n) - sum(phis), c)


def ma_weights(B: np.ndarray, n: int, p: int, h: int) -> np.ndarray:
    """Wold weights Psi_0, ..., Psi_h, with Psi_j = J F^j J'."""
    F = companion(B, n, p)
    J = np.zeros((n, n * p))
    J[:, :n] = np.eye(n)
    psis = np.empty((h + 1, n, n))
    power = np.eye(n * p)
    for j in range(h + 1):
        psis[j] = J @ power @ J.T
        power = power @ F
    return psis


def forecast(y: np.ndarray, B: np.ndarray, Sigma: np.ndarray, p: int, h: int = 12):
    """Point forecast and error variance by horizon (companion recursion).

    Returns (paths, variances) with shapes (h, n) and (h, n); the second is the
    diagonal of the mean squared error matrix at each horizon.
    """
    y = np.asarray(y, dtype=float)
    n = y.shape[1]
    phis, c = coefficients_by_lag(B, n, p)
    history = list(y[-p:][::-1])              # y_T, y_{T-1}, ...
    paths = np.empty((h, n))
    for step in range(h):
        nxt = c.copy()
        for lag, Phi in enumerate(phis):
            nxt = nxt + Phi @ history[lag]
        paths[step] = nxt
        history = [nxt] + history[:-1]
    psis = ma_weights(B, n, p, h - 1)
    variances = np.empty((h, n))
    cumulative = np.zeros((n, n))
    for step in range(h):
        cumulative = cumulative + psis[step] @ Sigma @ psis[step].T
        variances[step] = np.diag(cumulative)
    return paths, variances


def simulate(B: np.ndarray, Sigma: np.ndarray, n: int, p: int, T: int,
             burn: int = 100, seed: int | None = None) -> np.ndarray:
    """Simulate T observations of the VAR described by (B, Sigma)."""
    rng = np.random.default_rng(seed)
    phis, c = coefficients_by_lag(B, n, p)
    total = T + burn
    y = np.zeros((total, n))
    for t in range(p, total):
        value = c + rng.multivariate_normal(np.zeros(n), Sigma)
        for lag, Phi in enumerate(phis, start=1):
            value = value + Phi @ y[t - lag]
        y[t] = value
    return y[burn:]
