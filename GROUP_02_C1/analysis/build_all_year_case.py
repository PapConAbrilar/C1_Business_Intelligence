"""Build the C1 respiratory emergency case from all five official annual ZIPs.

The input extract retains uncleaned source rows for IdCausa 1 and 2. Prepared
tables remove duplicate facility/date/cause keys, keeping the first source row.
Run from the extracted package with ``--source-root data/source_cache`` after
retrieving the official ZIPs, or point ``--source-root`` at the repository root.
"""

from __future__ import annotations

import argparse
import gzip
from pathlib import Path
from zipfile import ZipFile

import pandas as pd


PACKAGE = Path(__file__).resolve().parents[1]
INPUT = PACKAGE / "data" / "input"
PROCESSED = PACKAGE / "data" / "processed"
AGE_COLS = ["Menores_1", "De_1_a_4", "De_5_a_14", "De_15_a_64", "De_65_y_mas"]
NUM_COLS = ["Total", *AGE_COLS]
SOURCE_COLS = [
    "IdEstablecimiento", "IdCausa", "Total", *AGE_COLS, "fecha", "semana",
    "GLOSATIPOESTABLECIMIENTO",
]
KEY = ["IdEstablecimiento", "fecha", "IdCausa"]


def read_year(source_root: Path, year: int, raw_output: gzip.GzipFile, write_header: bool) -> pd.DataFrame:
    """Keep every selected source row and write it before any cleaning."""
    archive_path = source_root / "Urgencias" / str(year) / f"AtencionesUrgencia{year}.zip"
    parts = []
    with ZipFile(archive_path) as archive, archive.open(f"AtencionesUrgencia{year}.csv") as raw:
        for chunk in pd.read_csv(
            raw, sep=";", encoding="latin1", usecols=SOURCE_COLS,
            dtype={"IdEstablecimiento": "string"}, chunksize=250_000,
            low_memory=False,
        ):
            selected = chunk.loc[chunk["IdCausa"].isin((1, 2)), SOURCE_COLS].copy()
            if selected.empty:
                continue
            selected.insert(0, "source_year", year)
            selected.to_csv(raw_output, index=False, header=write_header)
            write_header = False
            parts.append(selected)
    return pd.concat(parts, ignore_index=True)


def profile_and_prepare(selected: pd.DataFrame, year: int) -> tuple:
    """Profile raw rows, then retain one row per candidate event key."""
    parsed = pd.to_datetime(selected["fecha"], format="%d/%m/%Y", errors="coerce")
    numeric = selected[NUM_COLS].apply(pd.to_numeric, errors="coerce")
    duplicate = selected.duplicated(KEY, keep="first")
    missing_total = int(numeric["Total"].isna().sum())
    missing_age_cells = int(numeric[AGE_COLS].isna().sum().sum())
    age_mismatches = int((numeric["Total"] != numeric[AGE_COLS].sum(axis=1, min_count=5)).sum())
    invalid_week = int((~selected["semana"].between(1, 53)).sum())
    negative_cells = int((numeric < 0).sum().sum())
    dates_wrong_year = int((parsed.notna() & parsed.dt.year.ne(year)).sum())

    profile = {
        "year": year,
        "raw_selected_rows": len(selected),
        "unique_facilities": selected["IdEstablecimiento"].nunique(),
        "first_date": parsed.min().date().isoformat(),
        "last_date": parsed.max().date().isoformat(),
        "distinct_dates": parsed.nunique(),
        "missing_total": missing_total,
        "missing_age_cells": missing_age_cells,
        "age_sum_mismatches": age_mismatches,
        "negative_numeric_cells": negative_cells,
        "invalid_weeks": invalid_week,
        "invalid_dates": int(parsed.isna().sum()),
        "dates_outside_source_year": dates_wrong_year,
        "duplicate_key_extras": int(duplicate.sum()),
        "duplicate_all_visit_count": int(numeric.loc[duplicate & selected["IdCausa"].eq(1), "Total"].sum()),
        "duplicate_respiratory_count": int(numeric.loc[duplicate & selected["IdCausa"].eq(2), "Total"].sum()),
    }
    if any((missing_total, missing_age_cells, age_mismatches, negative_cells, invalid_week, parsed.isna().sum(), dates_wrong_year)):
        raise ValueError(f"Quality check needs review for {year}: {profile}")

    clean = selected.loc[~duplicate].copy()
    clean[NUM_COLS] = numeric.loc[~duplicate, NUM_COLS]
    clean["date"] = parsed.loc[~duplicate]
    clean["week_start"] = clean["date"] - pd.to_timedelta((clean["date"].dt.dayofweek + 1) % 7, unit="D")
    clean["facility_type"] = clean["GLOSATIPOESTABLECIMIENTO"].fillna("Unknown").astype(str).str.strip()
    clean.loc[clean["facility_type"].eq(""), "facility_type"] = "Unknown"

    # A source-year/week label is not a unique week at calendar boundaries.
    week_spans = (
        clean.groupby("semana", dropna=False)["week_start"].nunique().rename("distinct_week_starts")
    )
    collision = {
        "year": year,
        "source_week_labels_with_multiple_dates": int(week_spans.gt(1).sum()),
        "colliding_labels": ",".join(str(int(x)) for x in week_spans[week_spans.gt(1)].index),
    }

    annual = clean.groupby("IdCausa")["Total"].sum()
    annual_row = {
        "year": year,
        "all_emergency_visits": int(annual.get(1, 0)),
        "respiratory_visits": int(annual.get(2, 0)),
    }
    annual_row["respiratory_share_pct"] = 100 * annual_row["respiratory_visits"] / annual_row["all_emergency_visits"]

    resp = clean.loc[clean["IdCausa"].eq(2)]
    age = resp[AGE_COLS].sum().to_frame().T
    age.insert(0, "year", year)
    by_type = resp.groupby("facility_type", dropna=False)["Total"].sum().rename("respiratory_visits").reset_index()
    by_type.insert(0, "year", year)

    grouped = clean.groupby(
        ["week_start", "IdEstablecimiento", "facility_type", "IdCausa"],
        dropna=False, as_index=False,
    )[NUM_COLS].sum()
    grouped = grouped.rename(columns={
        "IdEstablecimiento": "facility_id", "IdCausa": "cause_id", "Total": "visits",
        "Menores_1": "under_1", "De_1_a_4": "age_1_4", "De_5_a_14": "age_5_14",
        "De_15_a_64": "age_15_64", "De_65_y_mas": "age_65_plus",
    })
    days = clean[["week_start", "date"]].drop_duplicates()
    return grouped, profile, collision, age, by_type, annual_row, days


def write_prepared_outputs(weekly_parts, profiles, collisions, ages, types, annuals, days_parts) -> None:
    """Write every derived table from already selected source rows."""
    PROCESSED.mkdir(parents=True, exist_ok=True)
    measure_cols = ["visits", "under_1", "age_1_4", "age_5_14", "age_15_64", "age_65_plus"]
    facility_week = pd.concat(weekly_parts, ignore_index=True).groupby(
        ["week_start", "facility_id", "facility_type", "cause_id"],
        dropna=False, as_index=False,
    )[measure_cols].sum()
    facility_week["week_end"] = facility_week["week_start"] + pd.Timedelta(days=6)
    facility_week["reporting_year"] = facility_week["week_end"].dt.year
    facility_week.to_csv(
        PROCESSED / "weekly_facility_cause_2020_2024.csv.gz",
        index=False, compression={"method": "gzip", "mtime": 0},
    )

    weekly = facility_week.groupby(["week_start", "week_end", "reporting_year", "cause_id"], as_index=False)[measure_cols].sum()
    weekly = weekly.pivot(index=["week_start", "week_end", "reporting_year"], columns="cause_id", values="visits").reset_index()
    weekly = weekly.rename(columns={1: "all_emergency_visits", 2: "respiratory_visits"})
    days = pd.concat(days_parts).drop_duplicates().groupby("week_start")["date"].nunique()
    weekly["observed_days"] = weekly["week_start"].map(days)
    weekly["complete_week"] = weekly["observed_days"].eq(7)
    weekly["respiratory_share_pct"] = 100 * weekly["respiratory_visits"] / weekly["all_emergency_visits"]
    annual_frame = pd.DataFrame(annuals)
    for field in ("all_emergency_visits", "respiratory_visits"):
        assert int(weekly[field].sum()) == int(annual_frame[field].sum()), field
    assert weekly[["all_emergency_visits", "respiratory_visits"]].notna().all().all()
    assert weekly["respiratory_visits"].le(weekly["all_emergency_visits"]).all()
    weekly.to_csv(PROCESSED / "weekly_national_2020_2024.csv", index=False)

    pd.DataFrame(profiles).to_csv(PROCESSED / "source_quality_profile.csv", index=False)
    pd.DataFrame(collisions).to_csv(PROCESSED / "source_week_collisions.csv", index=False)
    annual_frame.to_csv(PROCESSED / "annual_summary.csv", index=False)
    pd.concat(ages, ignore_index=True).to_csv(PROCESSED / "annual_respiratory_age_counts.csv", index=False)
    pd.concat(types, ignore_index=True).to_csv(PROCESSED / "annual_respiratory_facility_type.csv", index=False)

    # A missing cause-2 row is distinct from a reported zero.
    pairs = facility_week.groupby(["week_start", "facility_id", "facility_type"])["cause_id"].nunique()
    print(f"Facility-week units with only one of codes 1/2: {int(pairs.eq(1).sum()):,}")
    print(f"Saved {len(facility_week):,} facility-week-cause rows and {len(weekly)} national weeks")


def main(source_root: Path) -> None:
    INPUT.mkdir(parents=True, exist_ok=True)
    weekly_parts, profiles, collisions, ages, types, annuals, days_parts = [], [], [], [], [], [], []
    extract = INPUT / "emergency_id1_id2_all_dates_2020_2024.csv.gz"
    with gzip.open(extract, "wt", encoding="utf-8", newline="", compresslevel=6) as output:
        for year in range(2020, 2025):
            selected = read_year(source_root, year, output, write_header=year == 2020)
            weekly, profile, collision, age, by_type, annual, days = profile_and_prepare(selected, year)
            weekly_parts.append(weekly)
            profiles.append(profile)
            collisions.append(collision)
            ages.append(age)
            types.append(by_type)
            annuals.append(annual)
            days_parts.append(days)
            print(f"{year}: {len(selected):,} input rows; {profile['duplicate_key_extras']} duplicate-key extras")
    write_prepared_outputs(weekly_parts, profiles, collisions, ages, types, annuals, days_parts)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, default=PACKAGE / "data" / "source_cache")
    main(parser.parse_args().source_root)
