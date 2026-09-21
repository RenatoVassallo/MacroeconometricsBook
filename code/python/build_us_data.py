"""Build the US datasets used in the data and SVAR chapters.

The three workbooks are the samples distributed with the replication material
of Stock and Watson (2001), Blanchard and Quah (1989) and Uhlig (2005). The
four `fred_*.csv` files are FRED downloads, saved exactly as FRED serves them
(https://fred.stlouisfed.org/graph/fredgraph.csv?id=<SERIES>).
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


# FRED series used in chapters 0 and 1, grouped by frequency.
FRED = {
    "us_daily.csv": ("D", {"DEXUSEU": "usd_eur"}),
    "us_monthly.csv": ("M", {"UNRATENSA": "unemployment_nsa",
                             "FEDFUNDS": "fed_funds",
                             "CPIAUCNS": "cpi_nsa",
                             "PCEPI": "pce_price"}),
    "us_quarterly.csv": ("Q", {"GDPC1": "gdp",
                               "ND000334Q": "gdp_nsa"}),
}


def build_fred(freq: str, codes: dict[str, str]) -> pd.DataFrame:
    """Join FRED downloads of one frequency on a period index.

    Units: DEXUSEU, US dollars per euro (noon buying rates in New
    York; holidays are empty). UNRATENSA, unemployment rate, percent,
    not seasonally adjusted. FEDFUNDS, effective federal funds rate,
    monthly average, percent. CPIAUCNS, CPI for all urban consumers,
    1982-84 = 100, not seasonally adjusted. PCEPI, price index of
    personal consumption expenditures, 2017 = 100, seasonally
    adjusted. GDPC1, real GDP in billions of chained 2017 dollars,
    seasonally adjusted at annual rate. ND000334Q, the same concept
    not seasonally adjusted and not annualised (BEA publishes it
    only from 2002). October 2025 is missing in UNRATENSA and
    CPIAUCNS: the federal shutdown stopped data collection.
    """
    columns = {}
    for code, name in codes.items():
        raw = pd.read_csv(data_path(f"fred_{code}.csv", raw=True),
                          parse_dates=["observation_date"])
        values = raw.set_index("observation_date")[code]
        values.index = pd.PeriodIndex(values.index, freq=freq)
        columns[name] = values.astype(float)
    table = pd.DataFrame(columns)
    table.index.name = "date"
    return table


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
    for output, (freq, codes) in FRED.items():
        table = build_fred(freq, codes)
        target = data_path(output)
        table.to_csv(target, float_format="%.6f")
        print(f"{len(table)} obs, {table.index[0]} a {table.index[-1]}"
              f" -> {target}")
