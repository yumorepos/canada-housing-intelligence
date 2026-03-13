from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from analysis.city_metrics import clean_housing_data

REQUIRED_RAW_COLUMNS = {
    "city",
    "neighborhood",
    "year",
    "average_rent",
    "median_price",
}

OPTIONAL_DEFAULTS = {
    "borough": "Unknown",
    "listing_count": 0,
    "sales_count": 0,
    "coverage_score": 0.6,
    "property_type": "all",
}

PROVENANCE_COLUMNS = [
    "source_name",
    "source_type",
    "source_period",
    "processed_at",
    "coverage_note",
    "confidence_note",
    "data_mode",
]


def _derive_source_period(data: pd.DataFrame) -> str:
    years = pd.to_numeric(data["year"], errors="coerce").dropna()
    if years.empty:
        return "unknown"

    min_year = int(years.min())
    max_year = int(years.max())
    return str(min_year) if min_year == max_year else f"{min_year}-{max_year}"


def transform_raw_housing_data(
    raw_data: pd.DataFrame,
    *,
    source_name: str,
    source_type: str,
    source_period: str | None = None,
    coverage_note: str = "Coverage varies by city and neighborhood.",
    confidence_note: str = "Directional confidence only; not an official benchmark feed.",
    processed_at: str | None = None,
) -> pd.DataFrame:
    """Transform raw housing rows into the app-ready processed schema with provenance metadata."""
    missing = REQUIRED_RAW_COLUMNS.difference(raw_data.columns)
    if missing:
        raise ValueError(f"Raw dataset is missing required columns: {sorted(missing)}")

    transformed = raw_data.copy()

    for column, default in OPTIONAL_DEFAULTS.items():
        if column not in transformed.columns:
            transformed[column] = default

    transformed = clean_housing_data(transformed)

    transformed["source_name"] = source_name
    transformed["source_type"] = source_type
    transformed["source_period"] = source_period or _derive_source_period(transformed)
    transformed["processed_at"] = processed_at or datetime.now(UTC).isoformat(timespec="seconds")
    transformed["coverage_note"] = coverage_note
    transformed["confidence_note"] = confidence_note
    transformed["data_mode"] = "source_backed"

    return transformed


def process_raw_housing_file(
    raw_path: str,
    output_path: str,
    *,
    source_name: str,
    source_type: str,
    source_period: str | None = None,
    coverage_note: str = "Coverage varies by city and neighborhood.",
    confidence_note: str = "Directional confidence only; not an official benchmark feed.",
) -> pd.DataFrame:
    """Load local raw CSV data and write a processed app-compatible dataset."""
    raw_file = Path(raw_path)
    if not raw_file.exists():
        raise FileNotFoundError(f"Raw file not found at: {raw_path}")

    raw_data = pd.read_csv(raw_file)
    processed = transform_raw_housing_data(
        raw_data,
        source_name=source_name,
        source_type=source_type,
        source_period=source_period,
        coverage_note=coverage_note,
        confidence_note=confidence_note,
    )

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    processed.to_csv(output_file, index=False)
    return processed
