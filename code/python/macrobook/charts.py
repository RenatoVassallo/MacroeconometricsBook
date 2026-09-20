"""Recurring figures of the book.

Every function takes an `ax` (or creates one) and returns the matplotlib
object; the style comes from `styles/matplotlib.mplstyle` through `use_style`.
No function sets fonts or sizes: that lives in the style sheet.

Stacked charts use `PALETTE["fills"]`, not `PALETTE["shocks"]`: in a stacked
chart colour is the only thing separating one series from another, and the
design system's shock palette does not pass the colour-blindness check when two
fills touch. Line charts use the shock palette together with its line styles and
markers, which already provide a second signal.
"""

from __future__ import annotations

from typing import Sequence

import matplotlib.pyplot as plt
import numpy as np

from .style import PALETTE, use_style, figsize


def _ax(ax=None, **kwargs):
    use_style()
    if ax is None:
        _, ax = plt.subplots(**kwargs)
    return ax


# ---------------------------------------------------------------- episodes
def shade_episode(ax, start, end, kind: str = "recession", label=None):
    """Shade a span of the time axis (recession, forecast window, ...)."""
    color = PALETTE["episodes"].get(kind, PALETTE["episodes"]["recession"])
    return ax.axvspan(start, end, color=color, lw=0, zorder=0, label=label)


def zero_line(ax, y: float = 0.0):
    """Thin horizontal reference line."""
    return ax.axhline(y, color=PALETTE["ink"], lw=0.7, zorder=1)


def thousands(value: float, _=None) -> str:
    """Number with a thin space as the thousands separator: 12 500."""
    return f"{value:,.0f}".replace(",", "\u2009")


def year_ticks(ax, every: int = 1):
    """Year-only labels on a date axis, one every `every` years."""
    from matplotlib.dates import DateFormatter, YearLocator

    ax.xaxis.set_major_locator(YearLocator(every))
    ax.xaxis.set_major_formatter(DateFormatter("%Y"))
    return ax


def plain_log_ticks(ax, nticks: int = 5):
    """Label a logarithmic axis with round numbers instead of powers of ten.

    Matplotlib writes `6 x 10^3` on a log axis, which is unreadable in a book
    where the reader cares about the shape of the line, not about the decade.
    This picks round values inside the data range and writes them plainly.
    """
    from matplotlib.ticker import FixedLocator, FuncFormatter, NullLocator

    low, high = ax.get_ylim()
    steps = (1, 1.5, 2, 3, 4, 5, 6, 7, 8, 9)
    decades = range(int(np.floor(np.log10(low))),
                    int(np.ceil(np.log10(high))) + 1)
    candidates = [s * 10.0 ** d for d in decades for s in steps]
    candidates = [v for v in candidates if low <= v <= high]
    while len(candidates) > nticks:
        candidates = candidates[::2]
    ax.yaxis.set_major_locator(FixedLocator(candidates))
    ax.yaxis.set_minor_locator(NullLocator())
    ax.yaxis.set_major_formatter(FuncFormatter(thousands))
    return ax


def legend_outside(ax, ncol: int = 3, above: bool = False, **kwargs):
    """Frameless legend placed outside the data area.

    It is attached to the figure ("outside"), so the layout engine reserves the
    space and the legend never lands on top of the axis label.
    """
    fig = ax.figure
    handles, labels = ax.get_legend_handles_labels()
    loc = "outside upper center" if above else "outside lower center"
    return fig.legend(handles, labels, loc=loc, ncol=ncol, frameon=False, **kwargs)


def unit_circle(ax, roots, label="raíces de la companion"):
    """Eigenvalues of the companion form inside the unit circle."""
    ax = _ax(ax)
    angle = np.linspace(0, 2 * np.pi, 400)
    ax.plot(np.cos(angle), np.sin(angle), color=PALETTE["muted"], lw=0.8)
    roots = np.asarray(roots)
    ax.plot(roots.real, roots.imag, ls="none", marker="o", ms=5,
            markerfacecolor=PALETTE["accent"], markeredgecolor="white",
            markeredgewidth=0.6, label=label, zorder=3)
    ax.axhline(0, color=PALETTE["muted"], lw=0.5)
    ax.axvline(0, color=PALETTE["muted"], lw=0.5)
    ax.set_aspect("equal")
    ax.set_xlim(-1.15, 1.15)
    ax.set_ylim(-1.15, 1.15)
    ax.grid(False)
    ax.set_xlabel("parte real")
    ax.set_ylabel("parte imaginaria")
    return ax


# ---------------------------------------------------------------- fan chart
def fan_chart(ax, dates_hist, history, dates_fc, bands, median,
              realized=None, dates_realized=None, band_labels=None):
    """History, forecast median and predictive bands.

    `bands` is a sequence of (lower, upper) pairs ordered from the outermost to
    the innermost, for example [(q2.5, q97.5), (q16, q84)].
    """
    ax = _ax(ax)
    colors = PALETTE["bands"]
    n = len(bands)
    for i, (lo, hi) in enumerate(bands):
        color = colors[min(i, len(colors) - 1)]
        label = None if band_labels is None else band_labels[i]
        ax.fill_between(dates_fc, lo, hi, color=color, lw=0, zorder=2, label=label)
    ax.plot(dates_hist, history, color=PALETTE["ink"], lw=1.1, zorder=3, label="observado")
    ax.plot(dates_fc, median, color=PALETTE["accent_dark"], lw=1.3, ls=(0, (4, 2)),
            zorder=4, label="pronóstico")
    if realized is not None:
        ax.plot(dates_realized if dates_realized is not None else dates_fc,
                realized, ls="none", marker="o", ms=3.5,
                color=PALETTE["realized"], zorder=5, label="realizado")
    return ax


# ----------------------------------------------------------------- IRF grid
def _grid_size(rows: int):
    from .style import figsize as _figsize
    width = _figsize()[0]
    return (width, min(0.30 * width * rows + 0.12 * width, 2.2 * width))


def irf_grid(responses, variable_names: Sequence[str], shock_names: Sequence[str],
             bands=None, horizons=None, figsize=None, band_alpha: float = 0.5):
    """Impulse response grid: rows are variables, columns are shocks.

    Bands are drawn semi-transparent (`band_alpha`) so that the grid of the
    panel stays visible behind them.
    """
    use_style()
    nv, ns = len(variable_names), len(shock_names)
    h = horizons if horizons is not None else np.arange(len(responses[0][0]))
    size = figsize or _grid_size(nv)
    fig, axes = plt.subplots(nv, ns, figsize=size, sharex=True, squeeze=False)
    for i in range(nv):
        for j in range(ns):
            ax = axes[i][j]
            if bands is not None:
                pairs = bands[i][j]
                colors = PALETTE["bands"]
                for k, (lo, hi) in enumerate(pairs):
                    color = colors[min(k * (len(colors) - 1) // max(len(pairs) - 1, 1),
                                       len(colors) - 1)]
                    ax.fill_between(h, lo, hi, color=color, lw=0, zorder=2,
                                    alpha=band_alpha)
            ax.plot(h, responses[i][j], color=PALETTE["accent_dark"], lw=1.2, zorder=3)
            zero_line(ax)
            if i == 0:
                ax.set_title(shock_names[j], color=PALETTE["ink"], fontsize=8.5)
            if j == 0:
                ax.set_ylabel(variable_names[i])
    return fig, axes


# ------------------------------------------------------------------ stacked
def stacked(ax, dates, components: dict, series=None, series_label: str = "observado"):
    """Stacked decomposition (historical or of variance) with white separators."""
    ax = _ax(ax)
    colors = PALETTE["fills"]
    dates = np.asarray(dates)
    width = _bar_width(dates)
    cum_pos = np.zeros(len(dates))
    cum_neg = np.zeros(len(dates))
    for k, (name, values) in enumerate(components.items()):
        v = np.asarray(values, dtype=float)
        pos, neg = np.clip(v, 0, None), np.clip(v, None, 0)
        color = colors[k % len(colors)]
        ax.bar(dates, pos, bottom=cum_pos, width=width, color=color,
               edgecolor="white", linewidth=0.5, label=name, zorder=2)
        ax.bar(dates, neg, bottom=cum_neg, width=width, color=color,
               edgecolor="white", linewidth=0.5, zorder=2)
        cum_pos += pos
        cum_neg += neg
    if series is not None:
        ax.plot(dates, series, color=PALETTE["ink"], lw=1.2, zorder=3, label=series_label)
    zero_line(ax)
    ax.grid(False, axis="x")
    return ax


def _bar_width(dates) -> float:
    if len(dates) < 2:
        return 0.8
    try:
        step = np.diff(np.asarray(dates, dtype="datetime64[D]").astype(float)).min()
        return 0.85 * step
    except Exception:
        return 0.85 * float(np.diff(np.asarray(dates, dtype=float)).min())


# ------------------------------------------------------- densities and traces
def prior_posterior(ax, draws, prior_density=None, grid=None, ols_value=None,
                    label: str = "posterior"):
    """Posterior histogram, prior density and the OLS reference."""
    ax = _ax(ax)
    ax.hist(draws, bins=50, density=True, color=PALETTE["accent"], alpha=0.55,
            lw=0, label=label, zorder=2)
    if prior_density is not None and grid is not None:
        ax.plot(grid, prior_density, color=PALETTE["muted"], lw=1.2, label="prior", zorder=3)
    if ols_value is not None:
        ax.axvline(ols_value, color=PALETTE["ink"], lw=1.2, ls=(0, (4, 2)),
                   label="MCO", zorder=4)
    ax.grid(False, axis="x")
    return ax


def trace(ax, draws, burn: int = 0, label: str | None = None):
    """Chain trace with the burn-in shaded."""
    ax = _ax(ax)
    if burn:
        ax.axvspan(0, burn, color=PALETTE["surface_strong"], lw=0, zorder=0)
    ax.plot(np.arange(len(draws)), draws, color=PALETTE["steel"], lw=0.4,
            zorder=2, label=label)
    ax.grid(False, axis="x")
    return ax


def rmse_ratio(ax, horizons, series: dict, benchmark: float = 1.0):
    """RMSE relative to a benchmark model, by horizon.

    Each series carries its own colour, line style and marker, so it also reads
    in greyscale and in print.
    """
    ax = _ax(ax)
    for k, (name, values) in enumerate(series.items()):
        ax.plot(horizons, values,
                color=PALETTE["shocks"][k % len(PALETTE["shocks"])],
                ls=PALETTE["shock_linestyle"][k % len(PALETTE["shock_linestyle"])],
                marker=PALETTE["shock_marker"][k % len(PALETTE["shock_marker"])],
                ms=3.2, lw=1.1, label=name, zorder=2)
    ax.axhline(benchmark, color=PALETTE["ink"], lw=0.7, zorder=1)
    ax.set_xlabel("horizonte (trimestres)")
    return ax
