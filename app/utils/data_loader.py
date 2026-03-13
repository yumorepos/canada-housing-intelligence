from pathlib import Path
import pandas as pd


def load_housing_data(dataset_path: str) -> pd.DataFrame:
    """Load local housing dataset from CSV."""
    path = Path(dataset_path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found at: {dataset_path}")

    data = pd.read_csv(path)
    expected_columns = {"city", "neighborhood", "average_rent", "median_price", "year"}
    missing_columns = expected_columns.difference(data.columns)
    if missing_columns:
        raise ValueError(f"Dataset is missing required columns: {sorted(missing_columns)}")

    return data
