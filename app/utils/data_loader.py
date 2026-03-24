from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pandas as pd

from analysis.city_metrics import clean_housing_data


def _extract_provenance(data: pd.DataFrame) -> dict:
    if data.empty:
        return {
            "source_name": "unknown",
            "source_type": "unknown",
            "source_period": "unknown",
            "processed_at": "unknown",
            "data_mode": "sample",
        }

    def _first_or_unknown(column: str, default: str = "unknown") -> str:
        if column not in data.columns:
            return default
        values = [str(v) for v in data[column].dropna().astype(str).unique().tolist() if str(v).strip()]
        return values[0] if values else default

    data_mode = _first_or_unknown("data_mode", "sample")
    if data_mode == "unknown":
        data_mode = "sample"

    return {
        "source_name": _first_or_unknown("source_name", "local sample dataset"),
        "source_type": _first_or_unknown("source_type", "sample"),
        "source_period": _first_or_unknown("source_period"),
        "processed_at": _first_or_unknown("processed_at"),
        "coverage_note": _first_or_unknown("coverage_note", "Coverage is sample-based and directional."),
        "confidence_note": _first_or_unknown(
            "confidence_note",
            "Directional confidence only; not an official benchmark feed.",
        ),
        "data_mode": data_mode,
    }


def load_housing_dataset(dataset_path: str, fallback_path: str | None = None) -> tuple[pd.DataFrame, dict]:
    """Load housing data with optional fallback and return provenance metadata."""
    primary_path = Path(dataset_path)
    selected_path = primary_path

    if not primary_path.exists():
        if fallback_path is None:
            raise FileNotFoundError(f"Dataset not found at: {dataset_path}")
        fallback = Path(fallback_path)
        if not fallback.exists():
            raise FileNotFoundError(f"Dataset not found at: {dataset_path} (fallback missing at: {fallback_path})")
        selected_path = fallback

    raw_data = pd.read_csv(selected_path)
    cleaned = clean_housing_data(raw_data)
    provenance = _extract_provenance(cleaned)
    provenance["dataset_path"] = str(selected_path)
    provenance["record_count"] = int(len(cleaned))

    if selected_path != primary_path and provenance["data_mode"] == "source_backed":
        provenance["data_mode"] = "sample"

    processed_at_raw = provenance.get("processed_at")
    max_age_days = 45
    try:
        processed_at = datetime.fromisoformat(str(processed_at_raw).replace("Z", "+00:00"))
        if processed_at.tzinfo is None:
            processed_at = processed_at.replace(tzinfo=UTC)
        age_days = (datetime.now(UTC) - processed_at).days
        is_stale = age_days > max_age_days
        provenance["data_age_days"] = int(age_days)
        provenance["freshness_status"] = "stale" if is_stale else "fresh"
    except Exception:
        provenance["data_age_days"] = None
        provenance["freshness_status"] = "unknown"

    return cleaned, provenance


def load_housing_data(dataset_path: str) -> pd.DataFrame:
    """Backward-compatible loader that returns only cleaned housing rows."""
    data, _ = load_housing_dataset(dataset_path)
    return data
