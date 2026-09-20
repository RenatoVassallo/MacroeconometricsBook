"""Build the classic US datasets used in the data and SVAR chapters.

The three workbooks are the samples distributed with the replication material
of Stock and Watson (2001), Blanchard and Quah (1989) and Uhlig (2005).
Raw files are never edited: the tidy CSVs the chapters read are rebuilt from
`data/raw/` by running this script.

    uv run python code/python/build_us_data.py
"""

from __future__ import annotations

import pandas as pd

from macrobook import data_path

SOURCES = {
    "SW2001_Data.xlsx": ("sw2001.csv", ["unemp", "infl", "ff"]),
    "BQ1989_Data.xlsx": ("bq1989.csv", ["growth", "unemp"]),
    "Uhlig2005_Data.xlsx": ("uhlig2005.csv",
                            ["y", "pi", "comm", "res", "nbres", "ff"]),
}


def periods(stamp: pd.Series) -> pd.PeriodIndex:
    """Parse the '1960q1' and '1965m1' stamps used by the three workbooks."""
    text = stamp.str.upper().str.strip()
    if text.iloc[0].find("M") > 0:
        parts = text.str.split("M")
        return pd.PeriodIndex(parts.str[0] + "-" + parts.str[1].str.zfill(2),
                              freq="M")
    return pd.PeriodIndex(text, freq="Q")


def build(raw_file: str, columns: list[str]) -> pd.DataFrame:
    raw = pd.read_excel(data_path(raw_file, raw=True), header=None,
                        skiprows=2, names=["date"] + columns)
    raw["date"] = periods(raw["date"])
    return raw.set_index("date").astype(float)


if __name__ == "__main__":
    for raw_file, (output, columns) in SOURCES.items():
        table = build(raw_file, columns)
        target = data_path(output)
        target.parent.mkdir(parents=True, exist_ok=True)
        table.to_csv(target, float_format="%.6f")
        print(f"{len(table)} obs, {table.index[0]} a {table.index[-1]}"
              f" -> {target}")
