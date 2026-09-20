"""Build the quarterly Peruvian series used in the book.

Reads the raw workbook (BCRP data) and writes a small tidy CSV that the
chapters read. Raw data is never edited: everything downstream is rebuilt from
`data/raw/` by running this script.

    uv run python code/python/build_peru_data.py
"""

from __future__ import annotations

import pandas as pd

from macrobook import data_path

RAW_FILE = "database_peru.xlsx"
SHEET = "domestic"
COLUMNS = {"gdp": "gdp", "inf": "inf", "mpr": "mpr"}
OUTPUT = "peru_domestic.csv"


def build() -> pd.DataFrame:
    raw = pd.read_excel(data_path(RAW_FILE, raw=True), sheet_name=SHEET)
    raw["date"] = pd.PeriodIndex(pd.to_datetime(raw["date"]), freq="Q")
    table = raw.set_index("date")[list(COLUMNS)].rename(columns=COLUMNS).dropna()
    table.index.name = "date"
    return table


MONTHLY_RAW = "peru_mensual_bcrp.csv"
MONTHLY_COLUMNS = {"pbi": "gdp_sa", "ipc": "cpi", "tc": "fx", "tpm": "mpr"}
MONTHLY_OUTPUT = "peru_monthly.csv"


def build_monthly() -> pd.DataFrame:
    """Monthly BCRP series: GDP index (seasonally adjusted) and the CPI.

    Codes: PN01773AM (monthly GDP index, 2007 = 100, seasonally adjusted by
    the BCRP), PN38705PM (consumer price index of Metropolitan Lima, NOT
    seasonally adjusted), PN01210PM (exchange rate) and PD04722MM (policy
    rate).
    """
    raw = pd.read_csv(data_path(MONTHLY_RAW, raw=True), parse_dates=["date"])
    raw["date"] = pd.PeriodIndex(raw["date"], freq="M")
    table = raw.set_index("date")[list(MONTHLY_COLUMNS)]
    return table.rename(columns=MONTHLY_COLUMNS)


def write(table: pd.DataFrame, output: str) -> None:
    target = data_path(output)
    target.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(target, float_format="%.6f")
    print(f"{len(table)} obs, {table.index[0]} a {table.index[-1]}"
          f" -> {target}")


if __name__ == "__main__":
    write(build(), OUTPUT)
    write(build_monthly(), MONTHLY_OUTPUT)
