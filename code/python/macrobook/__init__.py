"""Helpers for the book *Macroeconometría aplicada con Python*.

Typical use at the top of a chapter:

    from macrobook import use_style, PALETTE, charts, var
    use_style()

`use_style` registers the book fonts, applies `styles/matplotlib.mplstyle` and
neutralises MacroPy's own styling, so every figure in the book comes out of the
same visual system.
"""

from .style import PALETTE, use_style, figsize, project_root, patch_macropy
from .data import data_path, save_figure
from . import charts, var, svar, bvar

__all__ = [
    "PALETTE",
    "use_style",
    "figsize",
    "project_root",
    "patch_macropy",
    "data_path",
    "save_figure",
    "charts",
    "var",
    "svar",
    "bvar",
]
