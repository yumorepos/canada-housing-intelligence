from pathlib import Path

import pandas as pd

from analysis.montreal import clean_housing_data


def load_housing_data(dataset_path: str) -> pd.DataFrame:
    """Load and validate local housing dataset from CSV."""
    path = Path(dataset_path)
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found at: {dataset_path}")

    raw_data = pd.read_csv(path)
    return clean_housing_data(raw_data)
