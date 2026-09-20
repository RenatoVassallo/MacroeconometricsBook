"""Bayesian VAR: Minnesota prior, Gibbs sampler and predictive draws.

Conventions follow `var.py`: `y` is (T, n), `B` is (k, n) with k = n*p + 1 and
the CONSTANT IN THE FIRST ROW, and the vectorised coefficient vector is
`b = vec(B)`, stacked by columns (equation by equation):

    y = (I_n kron X) b + u,   u ~ N(0, Sigma kron I_T).

The prior is the independent normal / inverse-Wishart pair

    b ~ N(b_0, H),   Sigma ~ IW(S_0, nu_0),

whose conditional posteriors are the two blocks of the Gibbs sampler.
"""

from __future__ import annotations

import numpy as np
from scipy.stats import invwishart

from .var import coefficients_by_lag, lag_matrix, ols


# --------------------------------------------------------------------- prior
def ar_residual_sd(y: np.ndarray, p: int) -> np.ndarray:
    """Residual standard deviation of a univariate AR(p) per variable."""
    y = np.asarray(y, dtype=float)
    sigma = np.empty(y.shape[1])
    for i in range(y.shape[1]):
        Y, X = lag_matrix(y[:, [i]], p)
        beta, *_ = np.linalg.lstsq(X, Y[:, 0], rcond=None)
        residual = Y[:, 0] - X @ beta
        sigma[i] = residual.std(ddof=X.shape[1])
    return sigma


def minnesota_prior(y: np.ndarray, p: int,
                    lam: tuple[float, float, float, float] = (0.2, 0.5, 1.0, 1e5),
                    delta: float | np.ndarray = 1.0):
    """Mean `b0` and covariance `H` of the Minnesota prior.

    `lam` holds (lambda_1, lambda_2, lambda_3, lambda_4): overall tightness,
    penalty on cross-variable lags, decay with the lag and the diffuse scale of
    the constant. `delta` is the prior mean of each variable's own first lag.
    Returns (b0, H) with H diagonal, both in vec(B) order.
    """
    y = np.asarray(y, dtype=float)
    n = y.shape[1]
    l1, l2, l3, l4 = lam
    delta = np.full(n, float(delta)) if np.isscalar(delta) else np.asarray(delta, float)
    sigma = ar_residual_sd(y, p)
    k = n * p + 1
    B0 = np.zeros((k, n))
    V = np.zeros((k, n))
    for i in range(n):                          # equation i
        V[0, i] = (sigma[i] * l4) ** 2          # constant: diffuse
        for lag in range(1, p + 1):
            for j in range(n):                  # variable j
                row = 1 + (lag - 1) * n + j
                if i == j:
                    if lag == 1:
                        B0[row, i] = delta[i]
                    V[row, i] = (l1 / lag ** l3) ** 2
                else:
                    V[row, i] = (l1 * l2 * sigma[i]
                                 / (lag ** l3 * sigma[j])) ** 2
    return B0.flatten(order="F"), np.diag(V.flatten(order="F"))


# ----------------------------------------------------------------- posterior
def posterior_coefficients(Y: np.ndarray, X: np.ndarray, b0: np.ndarray,
                           H: np.ndarray, Sigma: np.ndarray):
    """Mean and covariance of b | Sigma, Y (a precision-weighted average)."""
    H_inv = np.linalg.inv(H)
    Sigma_inv = np.linalg.inv(Sigma)
    precision = H_inv + np.kron(Sigma_inv, X.T @ X)
    V = np.linalg.inv(precision)
    signal = H_inv @ b0 + np.kron(Sigma_inv, X.T) @ Y.flatten(order="F")
    return V @ signal, V


def gibbs(y: np.ndarray, p: int, b0: np.ndarray, H: np.ndarray,
          draws: int = 5000, burn: int = 2000, S0: np.ndarray | None = None,
          nu0: int | None = None, stable_only: bool = True,
          seed: int | None = None):
    """Draws from the posterior of (b, Sigma) with the two-block Gibbs sampler.

    Returns (draws_b, draws_Sigma) with shapes (kept, n*k) and (kept, n, n).
    Explosive draws are discarded when `stable_only`, as is standard when the
    posterior is used for impulse responses or unconditional moments.
    """
    y = np.asarray(y, dtype=float)
    Y, X = lag_matrix(y, p)
    T_eff, n = Y.shape
    k = X.shape[1]
    S0 = np.eye(n) if S0 is None else S0
    nu0 = n + 1 if nu0 is None else nu0
    rng = np.random.default_rng(seed)
    Sigma = ols(y, p)["Sigma"]
    kept_b, kept_S = [], []
    for step in range(draws):
        mean, V = posterior_coefficients(Y, X, b0, H, Sigma)
        b = rng.multivariate_normal(mean, (V + V.T) / 2)
        B = b.reshape((k, n), order="F")
        if stable_only:
            phis, _ = coefficients_by_lag(B, n, p)
            F = np.zeros((n * p, n * p))
            F[:n] = np.hstack(phis)
            if p > 1:
                F[n:, : n * (p - 1)] = np.eye(n * (p - 1))
            if np.max(np.abs(np.linalg.eigvals(F))) >= 1:
                continue
        E = Y - X @ B
        Sigma = invwishart.rvs(df=nu0 + T_eff, scale=S0 + E.T @ E,
                               random_state=rng)
        if step >= burn:
            kept_b.append(b)
            kept_S.append(Sigma)
    return np.array(kept_b), np.array(kept_S)


# ---------------------------------------------------------------- prediction
def predictive_draws(draws_b, draws_Sigma, y: np.ndarray, p: int, h: int = 12,
                     seed: int | None = None) -> np.ndarray:
    """Predictive density: one path per posterior draw, shape (draws, h, n)."""
    y = np.asarray(y, dtype=float)
    n = y.shape[1]
    k = n * p + 1
    rng = np.random.default_rng(seed)
    paths = np.empty((len(draws_b), h, n))
    for s, (b, Sigma) in enumerate(zip(draws_b, draws_Sigma)):
        B = b.reshape((k, n), order="F")
        history = y[-p:].copy()
        for step in range(h):
            x = np.concatenate([[1.0], history[::-1].ravel()])
            shock = rng.multivariate_normal(np.zeros(n), Sigma)
            nxt = x @ B + shock
            paths[s, step] = nxt
            history = np.vstack([history[1:], nxt])
    return paths


def posterior_mean_forecast(y: np.ndarray, p: int, b0: np.ndarray,
                            H: np.ndarray, h: int = 12,
                            Sigma: np.ndarray | None = None) -> np.ndarray:
    """Point forecast from the posterior mean with Sigma held fixed.

    Litterman's original device: with Sigma treated as known there is no need
    to simulate, which makes rolling out-of-sample exercises cheap.
    """
    from .var import forecast

    y = np.asarray(y, dtype=float)
    n = y.shape[1]
    k = n * p + 1
    fit = ols(y, p)
    Sigma = fit["Sigma"] if Sigma is None else Sigma
    Y, X = lag_matrix(y, p)
    mean, _ = posterior_coefficients(Y, X, b0, H, Sigma)
    B = mean.reshape((k, n), order="F")
    paths, _ = forecast(y, B, Sigma, p, h)
    return paths
