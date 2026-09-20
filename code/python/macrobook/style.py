"""Single visual system for every figure in the book (Warm Folio)."""

from __future__ import annotations

import warnings
from pathlib import Path

import matplotlib as mpl
import matplotlib.font_manager as fm
import matplotlib.pyplot as plt

# --------------------------------------------------------------------------
# Palette. The values come from styles/design/tokens.json; when they change
# there they must change here, in styles/book.scss and in styles/book.tex.
# --------------------------------------------------------------------------
PALETTE = {
    "ink": "#2A231D",
    "muted": "#6B5F52",
    "paper": "#FDFBF7",
    "surface": "#F7EDE5",
    "surface_strong": "#F0E0D6",
    "rule": "#DED0C4",
    "grid": "#E7DAD0",
    "accent": "#B0472A",
    "accent_dark": "#8E3620",
    "olive": "#4E6E38",
    "steel": "#3D647F",
    # series
    "observed": ["#2A231D", "#6B5F52", "#9A9086"],
    "estimate": ["#B0472A", "#8E3620"],
    "realized": "#1F3D5C",
    # bands: 0 = outermost, 3 = innermost
    "bands": ["#F4DCD1", "#E6BCA8", "#D4907A", "#BF6244"],
    "shocks": ["#2A231D", "#3D647F", "#B0472A", "#5A7D43", "#9A7B2E", "#C9A98A"],
    "shock_linestyle": ["-", "--", "-.", ":", (0, (6, 2)), "-"],
    "shock_marker": ["o", "s", "^", "D", "v", "o"],
    # Fills for stacked charts (historical decomposition, FEVD). In a stacked
    # chart colour is the only thing separating one series from another, and
    # the design system's shock palette fails the colour-blindness check when
    # two fills touch; this one passes. See styles/design/NOTAS-IMPLEMENTACION.md.
    "fills": ["#2F7CA8", "#C4522A", "#BE8C1F", "#2E8B62", "#8E5AA6", "#9A9086"],
    "diverging": ["#8E3620", "#C06A4A", "#E2AC93", "#F0E0D6",
                  "#9DB6C6", "#5B87A3", "#23435A"],
    # Sombreados neutros: el de pronóstico no debe confundirse con las bandas.
    "episodes": {"recession": "#E7E3DD", "forecast": "#F1EFEB"},
}

_APPLIED = False


def figsize(ratio: float = 0.58, width: float | None = None):
    """Figure size (width, height) in inches, with height = ratio * width.

    The width comes from Quarto, which sets `figure.figsize` per format: 7 in
    for the web and 4.5 in for the PDF. Chapters therefore never hardcode a
    width, and the same code produces a figure that fits each medium with the
    same point sizes.
    """
    if width is None:
        width = plt.rcParams["figure.figsize"][0]
    return (width, ratio * width)


def project_root(start: Path | str | None = None) -> Path:
    """Repository root: the folder that holds _quarto.yml."""
    current = Path(start or Path.cwd()).resolve()
    for candidate in [current, *current.parents]:
        if (candidate / "_quarto.yml").exists():
            return candidate
    return current


def _register_fonts(root: Path) -> None:
    folder = root / "styles" / "fonts"
    if not folder.exists():
        warnings.warn(f"Fonts not found in {folder}.")
        return
    for file in sorted(folder.glob("*.ttf")):
        try:
            fm.fontManager.addfont(str(file))
        except Exception as exc:  # pragma: no cover
            warnings.warn(f"Could not register {file.name}: {exc}")


def patch_macropy() -> None:
    """Stop MacroPy from re-imposing its own style.

    MacroPy's plotting functions call `set_bse_style()`, which overwrites the
    rcParams (serif font, BSE palette) on every call. Here it is replaced by a
    no-op and its colour constants are pointed at the book palette, so that
    `styles/matplotlib.mplstyle` stays the single source of style.
    """
    try:
        from MacroPy import plots_kalman
    except Exception:
        return

    modules = [plots_kalman]
    for name in ("plots_uc", "plots_tvarsv"):
        try:
            modules.append(__import__(f"MacroPy.{name}", fromlist=[name]))
        except Exception:
            pass

    mapping = {
        "BSE_TEAL": PALETTE["ink"],
        "BSE_TEAL_SOFT": PALETTE["muted"],
        "BSE_ORANGE": PALETTE["accent"],
        "BSE_NAVY": PALETTE["steel"],
        "BSE_GRAY": PALETTE["muted"],
        "BSE_LIGHT": PALETTE["surface"],
    }
    for module in modules:
        if hasattr(module, "set_bse_style"):
            module.set_bse_style = lambda: None
        for key, value in mapping.items():
            if hasattr(module, key):
                setattr(module, key, value)


def use_style(force: bool = False) -> None:
    """Apply the book style to matplotlib. Idempotent."""
    global _APPLIED
    if _APPLIED and not force:
        return
    root = project_root()
    _register_fonts(root)
    sheet = root / "styles" / "matplotlib.mplstyle"
    if sheet.exists():
        plt.style.use(str(sheet))
    else:  # pragma: no cover
        warnings.warn(f"{sheet} not found; figures will use matplotlib defaults.")
    if "Source Sans 3" not in {f.name for f in fm.fontManager.ttflist}:
        warnings.warn("Source Sans 3 is not registered; matplotlib will substitute a font.")
    mpl.colormaps.register(
        mpl.colors.LinearSegmentedColormap.from_list("warmfolio_div", PALETTE["diverging"]),
        force=True,
    )
    patch_macropy()
    _APPLIED = True
