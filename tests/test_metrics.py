import pandas as pd

from analysis.montreal import calculate_city_kpis, clean_housing_data, neighborhood_affordability_snapshot
from app.utils.metrics import calculate_housing_metrics


def test_clean_housing_data_standardizes_and_sorts():
    df = pd.DataFrame(
        {
            "city": [" Montreal "],
            "neighborhood": [" Plateau "],
            "year": ["2022"],
            "average_rent": ["1500"],
            "median_price": ["550000"],
        }
    )

    cleaned = clean_housing_data(df)

    assert cleaned.loc[0, "city"] == "Montreal"
    assert cleaned.loc[0, "neighborhood"] == "Plateau"
    assert cleaned.loc[0, "year"] == 2022


def test_calculate_housing_metrics_returns_growth_values():
    df = pd.DataFrame(
        {
            "city": ["Montreal", "Montreal"],
            "neighborhood": ["A", "A"],
            "year": [2020, 2021],
            "average_rent": [1000, 1100],
            "median_price": [400000, 440000],
        }
    )

    metrics = calculate_housing_metrics(df, "Montreal")

    assert round(metrics["rent_growth_pct"], 1) == 10.0
    assert round(metrics["price_growth_pct"], 1) == 10.0


def test_affordability_snapshot_adds_ratio_column():
    df = pd.DataFrame(
        {
            "city": ["Montreal", "Montreal"],
            "neighborhood": ["A", "B"],
            "year": [2023, 2023],
            "average_rent": [1200, 1800],
            "median_price": [400000, 600000],
        }
    )

    snapshot = neighborhood_affordability_snapshot(df, "Montreal")

    assert "rent_to_price_ratio" in snapshot.columns
    assert snapshot.iloc[0]["average_rent"] == 1800


def test_calculate_city_kpis_returns_latest_year():
    df = pd.DataFrame(
        {
            "city": ["Montreal", "Montreal", "Montreal"],
            "neighborhood": ["A", "A", "A"],
            "year": [2021, 2022, 2023],
            "average_rent": [1000, 1100, 1200],
            "median_price": [400000, 420000, 450000],
        }
    )

    kpis = calculate_city_kpis(df, "Montreal")

    assert kpis["latest_year"] == 2023
