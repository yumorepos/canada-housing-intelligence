from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
import yaml

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


def load_data_contract(contract_path: str = "config/data_contract.yml") -> dict:
    path = Path(contract_path)
    if not path.exists():
        raise FileNotFoundError(f"Data contract not found at: {contract_path}")

    with path.open("r", encoding="utf-8") as file:
        contract = yaml.safe_load(file) or {}

    required = contract.get("required_columns")
    if not isinstance(required, dict) or not required:
        raise ValueError("Data contract must include non-empty 'required_columns'.")

    return contract


def _validate_required_column_values(data: pd.DataFrame, column: str, rules: dict) -> None:
    column_data = data[column]

    if rules.get("allow_empty") is False and column_data.astype(str).str.strip().eq("").any():
        raise ValueError(f"Column '{column}' contains empty values but allow_empty=false.")

    if "min" in rules:
        if pd.to_numeric(column_data, errors="coerce").lt(rules["min"]).any():
            raise ValueError(f"Column '{column}' contains values below minimum {rules['min']}.")

    if "max" in rules:
        if pd.to_numeric(column_data, errors="coerce").gt(rules["max"]).any():
            raise ValueError(f"Column '{column}' contains values above maximum {rules['max']}.")


def validate_raw_data_contract(raw_data: pd.DataFrame, contract: dict) -> None:
    required = contract.get("required_columns", {})
    missing = set(required.keys()).difference(raw_data.columns)
    if missing:
        raise ValueError(f"Raw dataset is missing required columns from contract: {sorted(missing)}")

    for column, rules in required.items():
        expected_type = str((rules or {}).get("type", "")).lower()
        if expected_type in {"integer", "number"}:
            converted = pd.to_numeric(raw_data[column], errors="coerce")
            if converted.isna().any():
                raise ValueError(f"Column '{column}' must be numeric per contract type '{expected_type}'.")
            if expected_type == "integer" and not converted.mod(1).eq(0).all():
                raise ValueError(f"Column '{column}' must be integer per contract.")
        _validate_required_column_values(raw_data, column, rules or {})


def _derive_source_period(data: pd.DataFrame) -> str:
    years = pd.to_numeric(data["year"], errors="coerce").dropna()
    if years.empty:
        return "unknown"

    min_year = int(years.min())
    max_year = int(years.max())
    return str(min_year) if min_year == max_year else f"{min_year}-{max_year}"


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_processing_manifest(
    *,
    raw_file: Path,
    output_file: Path,
    processed_rows: int,
    source_name: str,
    source_type: str,
    source_period: str | None,
    data_contract_path: str,
    manifest_path: str | None = None,
) -> Path:
    timestamp = datetime.now(UTC).isoformat(timespec="seconds")
    default_manifest = (
        output_file.parent
        / "manifests"
        / f"{output_file.stem}_{datetime.now(UTC).strftime('%Y%m%dT%H%M%SZ')}.json"
    )
    destination = Path(manifest_path) if manifest_path else default_manifest
    destination.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "processed_at": timestamp,
        "raw_path": str(raw_file),
        "output_path": str(output_file),
        "raw_sha256": _file_sha256(raw_file),
        "output_sha256": _file_sha256(output_file),
        "processed_rows": int(processed_rows),
        "source_name": source_name,
        "source_type": source_type,
        "source_period": source_period or "auto",
        "data_contract_path": data_contract_path,
    }

    destination.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return destination


def transform_raw_housing_data(
    raw_data: pd.DataFrame,
    *,
    source_name: str,
    source_type: str,
    data_contract: dict | None = None,
    source_period: str | None = None,
    coverage_note: str = "Coverage varies by city and neighborhood.",
    confidence_note: str = "Directional confidence only; not an official benchmark feed.",
    processed_at: str | None = None,
) -> pd.DataFrame:
    """Transform raw housing rows into the app-ready processed schema with provenance metadata."""
    contract_required = set((data_contract or {}).get("required_columns", {}).keys())
    required_columns = contract_required or REQUIRED_RAW_COLUMNS
    missing = required_columns.difference(raw_data.columns)
    if missing:
        raise ValueError(f"Raw dataset is missing required columns: {sorted(missing)}")

    if data_contract is not None:
        validate_raw_data_contract(raw_data, data_contract)

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
    data_contract_path: str = "config/data_contract.yml",
    manifest_path: str | None = None,
    source_period: str | None = None,
    coverage_note: str = "Coverage varies by city and neighborhood.",
    confidence_note: str = "Directional confidence only; not an official benchmark feed.",
) -> pd.DataFrame:
    """Load local raw CSV data and write a processed app-compatible dataset."""
    raw_file = Path(raw_path)
    if not raw_file.exists():
        raise FileNotFoundError(f"Raw file not found at: {raw_path}")

    raw_data = pd.read_csv(raw_file)
    contract = load_data_contract(data_contract_path)
    processed = transform_raw_housing_data(
        raw_data,
        source_name=source_name,
        source_type=source_type,
        data_contract=contract,
        source_period=source_period,
        coverage_note=coverage_note,
        confidence_note=confidence_note,
    )

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    processed.to_csv(output_file, index=False)
    write_processing_manifest(
        raw_file=raw_file,
        output_file=output_file,
        processed_rows=len(processed),
        source_name=source_name,
        source_type=source_type,
        source_period=source_period,
        data_contract_path=data_contract_path,
        manifest_path=manifest_path,
    )
    return processed
