from pathlib import Path

import pandas as pd
import pytest

from app.utils.data_loader import load_housing_dataset
from app.utils.ingestion import (
    load_data_contract,
    process_raw_housing_file,
    transform_raw_housing_data,
    validate_raw_data_contract,
)


def test_transform_raw_housing_data_adds_provenance_columns():
    raw = pd.DataFrame(
        {
            "city": ["Montreal"],
            "neighborhood": ["Plateau"],
            "year": [2022],
            "average_rent": [1800],
            "median_price": [620000],
        }
    )

    transformed = transform_raw_housing_data(
        raw,
        source_name="Test Source",
        source_type="manual_csv_drop",
        processed_at="2026-01-01T00:00:00+00:00",
    )

    assert transformed.loc[0, "source_name"] == "Test Source"
    assert transformed.loc[0, "source_type"] == "manual_csv_drop"
    assert transformed.loc[0, "source_period"] == "2022"
    assert transformed.loc[0, "processed_at"] == "2026-01-01T00:00:00+00:00"
    assert transformed.loc[0, "data_mode"] == "source_backed"


def test_process_raw_housing_file_writes_output(tmp_path: Path):
    raw_path = tmp_path / "raw.csv"
    out_path = tmp_path / "processed.csv"
    pd.DataFrame(
        {
            "city": ["Toronto"],
            "neighborhood": ["Downtown"],
            "year": [2021],
            "average_rent": [2100],
            "median_price": [850000],
        }
    ).to_csv(raw_path, index=False)

    processed = process_raw_housing_file(
        raw_path=str(raw_path),
        output_path=str(out_path),
        source_name="Test Source",
        source_type="csv_extract",
    )

    assert out_path.exists()
    assert len(processed) == 1
    manifests = list((tmp_path / "manifests").glob("*.json"))
    assert len(manifests) == 1


def test_load_housing_dataset_falls_back_to_sample(tmp_path: Path):
    fallback = tmp_path / "fallback.csv"
    pd.DataFrame(
        {
            "city": ["Vancouver"],
            "neighborhood": ["Kitsilano"],
            "year": [2020],
            "average_rent": [2000],
            "median_price": [900000],
        }
    ).to_csv(fallback, index=False)

    data, provenance = load_housing_dataset("missing.csv", fallback_path=str(fallback))

    assert len(data) == 1
    assert provenance["data_mode"] == "sample"
    assert provenance["dataset_path"] == str(fallback)


def test_transform_raw_housing_data_validates_required_columns():
    raw = pd.DataFrame({"city": ["Montreal"]})
    with pytest.raises(ValueError, match="missing required columns"):
        transform_raw_housing_data(raw, source_name="X", source_type="Y")


def test_load_data_contract_requires_required_columns(tmp_path: Path):
    contract_path = tmp_path / "data_contract.yml"
    contract_path.write_text("version: 1\n", encoding="utf-8")

    with pytest.raises(ValueError, match="required_columns"):
        load_data_contract(str(contract_path))


def test_validate_raw_data_contract_enforces_numeric_types():
    contract = {
        "required_columns": {
            "city": {"type": "string"},
            "neighborhood": {"type": "string"},
            "year": {"type": "integer"},
            "average_rent": {"type": "number"},
            "median_price": {"type": "number"},
        }
    }
    raw = pd.DataFrame(
        {
            "city": ["Montreal"],
            "neighborhood": ["Plateau"],
            "year": ["not-a-year"],
            "average_rent": [1800],
            "median_price": [620000],
        }
    )

    with pytest.raises(ValueError, match="must be numeric"):
        validate_raw_data_contract(raw, contract)


def test_load_housing_dataset_marks_unknown_freshness_without_processed_at(tmp_path: Path):
    fallback = tmp_path / "fallback.csv"
    pd.DataFrame(
        {
            "city": ["Vancouver"],
            "neighborhood": ["Kitsilano"],
            "year": [2020],
            "average_rent": [2000],
            "median_price": [900000],
        }
    ).to_csv(fallback, index=False)

    _, provenance = load_housing_dataset("missing.csv", fallback_path=str(fallback))

    assert provenance["freshness_status"] == "unknown"
    assert provenance["data_age_days"] is None


def test_load_housing_dataset_marks_stale_when_processed_at_old(tmp_path: Path):
    fallback = tmp_path / "fallback.csv"
    pd.DataFrame(
        {
            "city": ["Toronto"],
            "neighborhood": ["Downtown"],
            "year": [2024],
            "average_rent": [2500],
            "median_price": [950000],
            "processed_at": ["2020-01-01T00:00:00+00:00"],
        }
    ).to_csv(fallback, index=False)

    _, provenance = load_housing_dataset("missing.csv", fallback_path=str(fallback))

    assert provenance["freshness_status"] == "stale"
    assert provenance["data_age_days"] > 45


def test_load_housing_dataset_respects_custom_max_age_days(tmp_path: Path):
    fallback = tmp_path / "fallback.csv"
    pd.DataFrame(
        {
            "city": ["Toronto"],
            "neighborhood": ["Downtown"],
            "year": [2024],
            "average_rent": [2500],
            "median_price": [950000],
            "processed_at": ["2026-03-01T00:00:00+00:00"],
        }
    ).to_csv(fallback, index=False)

    _, provenance = load_housing_dataset("missing.csv", fallback_path=str(fallback), max_age_days=10)

    assert provenance["freshness_status"] == "stale"
    assert provenance["data_age_days"] >= 20
