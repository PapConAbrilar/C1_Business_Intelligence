"""Profile the included, uncleaned five-year reduced input.

This script is deliberately independent of the annual source ZIPs. It preserves
recorded zeros and checks the facility/date/cause unit before any aggregation.
"""

from pathlib import Path

import pandas as pd


PACKAGE = Path(__file__).resolve().parents[1]
INPUT = PACKAGE / "data/input/emergency_id1_id2_all_dates_2020_2024.csv.gz"
OUTPUT = PACKAGE / "data/processed/reduced_input_profile.csv"
KEY = ["source_year", "IdEstablecimiento", "fecha", "IdCausa"]
AGES = ["Menores_1", "De_1_a_4", "De_5_a_14", "De_15_a_64", "De_65_y_mas"]


def main() -> None:
    data = pd.read_csv(INPUT, dtype={"IdEstablecimiento": "string"}, low_memory=False)
    rows = []
    for (year, cause), group in data.groupby(["source_year", "IdCausa"], sort=True):
        parsed_dates = pd.to_datetime(group["fecha"], format="%d/%m/%Y", errors="coerce")
        rows.append({
            "year": year,
            "cause_id": cause,
            "rows": len(group),
            "facilities": group["IdEstablecimiento"].nunique(),
            "dates": parsed_dates.nunique(),
            "first_date": parsed_dates.min().date().isoformat(),
            "last_date": parsed_dates.max().date().isoformat(),
            "missing_key_cells": int(group[KEY].isna().sum().sum()),
            "missing_measure_cells": int(group[["Total", *AGES]].isna().sum().sum()),
            "missing_facility_type": int(group["GLOSATIPOESTABLECIMIENTO"].isna().sum()),
            "recorded_zero_total_rows": int(group["Total"].eq(0).sum()),
            "duplicate_key_extras": int(group.duplicated(KEY, keep="first").sum()),
            "age_sum_mismatches": int(group["Total"].ne(group[AGES].sum(axis=1)).sum()),
        })

    clean = data.drop_duplicates(KEY, keep="first")
    pairs = clean.pivot(
        index=["source_year", "IdEstablecimiento", "fecha"],
        columns="IdCausa", values="Total",
    )
    if pairs.isna().any().any():
        raise ValueError("At least one facility/date is missing cause 1 or 2")
    if pairs[2].gt(pairs[1]).any():
        raise ValueError("At least one respiratory count exceeds all visits")

    profile = pd.DataFrame(rows)
    profile.to_csv(OUTPUT, index=False)
    print(profile.to_string(index=False))
    print(f"Paired facility dates: {len(pairs):,}; missing cause rows: 0; respiratory > all: 0")


if __name__ == "__main__":
    main()
