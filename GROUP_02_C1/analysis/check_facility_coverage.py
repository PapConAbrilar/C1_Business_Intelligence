"""Check reporting coverage and a common-facility sensitivity case.

Reads the included uncleaned IdCausa 1/2 extract, so the reviewer can run this
without downloading the full annual DEIS archives.
"""

from pathlib import Path

import pandas as pd


PACKAGE = Path(__file__).resolve().parents[1]
SOURCE = PACKAGE / "data" / "input" / "emergency_id1_id2_all_dates_2020_2024.csv.gz"
OUTPUT = PACKAGE / "data" / "processed"
KEY = ["source_year", "IdEstablecimiento", "fecha", "IdCausa"]


def main() -> None:
    data = pd.read_csv(
        SOURCE,
        usecols=[*KEY, "Total"],
        dtype={"IdEstablecimiento": "string"},
    )
    data = data.drop_duplicates(KEY, keep="first")
    all_visit = data.loc[data["IdCausa"].eq(1)]
    days = all_visit.groupby(["source_year", "IdEstablecimiento"])["fecha"].nunique()
    coverage = days.groupby("source_year").agg(
        reporting_facilities="size",
        median_reporting_days="median",
        tenth_percentile_reporting_days=lambda x: x.quantile(0.1),
        facilities_under_100_days=lambda x: int(x.lt(100).sum()),
        facilities_at_least_300_days=lambda x: int(x.ge(300).sum()),
    ).reset_index().rename(columns={"source_year": "year"})
    coverage.to_csv(OUTPUT / "facility_reporting_coverage.csv", index=False)

    sets = [set(group["IdEstablecimiento"].dropna()) for _, group in all_visit.groupby("source_year")]
    common = set.intersection(*sets)
    annual = data.groupby(["source_year", "IdCausa"])["Total"].sum().unstack()
    stable = data.loc[data["IdEstablecimiento"].isin(common)].groupby(
        ["source_year", "IdCausa"]
    )["Total"].sum().unstack()
    sensitivity = pd.DataFrame({
        "year": annual.index,
        "common_facilities": len(common),
        "all_facility_share_pct": 100 * annual[2] / annual[1],
        "common_facility_share_pct": 100 * stable[2] / stable[1],
        "common_facility_all_visit_coverage_pct": 100 * stable[1] / annual[1],
    }).reset_index(drop=True)
    sensitivity.to_csv(OUTPUT / "common_facility_sensitivity.csv", index=False)
    print(coverage.to_string(index=False))
    print(sensitivity.round(2).to_string(index=False))


if __name__ == "__main__":
    main()
