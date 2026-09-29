"""Rebuild all derived C1 tables from the included uncleaned reduced input.

This is the normal reviewer route: the five large DEIS annual ZIPs are not needed.
The source-ZIP route in build_all_year_case.py creates the same selected extract.
"""

from pathlib import Path

import pandas as pd

from build_all_year_case import profile_and_prepare, write_prepared_outputs


PACKAGE = Path(__file__).resolve().parents[1]
SOURCE = PACKAGE / "data/input/emergency_id1_id2_all_dates_2020_2024.csv.gz"


def main() -> None:
    data = pd.read_csv(SOURCE, dtype={"IdEstablecimiento": "string"}, low_memory=False)
    expected_years = list(range(2020, 2025))
    if sorted(data["source_year"].unique().tolist()) != expected_years:
        raise ValueError("Reduced input does not contain exactly the five local years")
    outputs = [[] for _ in range(7)]
    for year, selected in data.groupby("source_year", sort=True):
        for bucket, result in zip(outputs, profile_and_prepare(selected, year)):
            bucket.append(result)
    write_prepared_outputs(*outputs)
    print(f"Rebuilt from included reduced input: {len(data):,} rows")


if __name__ == "__main__":
    main()
