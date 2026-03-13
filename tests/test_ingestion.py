from pathlib import Path

import pandas as pd
import pytest

from app.utils.data_loader import load_housing_dataset
from app.utils.ingestion import process_raw_housing_file, transform_raw_housing_data


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
