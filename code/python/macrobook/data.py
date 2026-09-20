"""Data paths and figure saving."""

from __future__ import annotations

from pathlib import Path

from .style import project_root


def data_path(name: str = "", raw: bool = False) -> Path:
    """Path inside `data/processed` (default) or `data/raw`.

    Raw data is never edited: it is downloaded into `data/raw` and everything
    else is built in `data/processed`.
    """
    base = project_root() / "data" / ("raw" if raw else "processed")
    return base / name if name else base


def save_figure(fig, name: str, formats=("pdf", "svg")) -> list[Path]:
    """Save a figure into `figures/generated/`.

    Only for figures produced by a script in `code/`. Figures created inside a
    chapter are written by Quarto.
    """
    target = project_root() / "figures" / "generated"
    target.mkdir(parents=True, exist_ok=True)
    paths = []
    for fmt in formats:
        path = target / f"{name}.{fmt}"
        fig.savefig(path)
        paths.append(path)
    return paths
