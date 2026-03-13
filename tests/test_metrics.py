import pandas as pd

from app.utils.metrics import calculate_housing_metrics


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
