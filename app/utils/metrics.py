import pandas as pd

from analysis.montreal import calculate_city_kpis


def calculate_housing_metrics(data: pd.DataFrame, city: str) -> dict:
    """Backward-compatible metrics wrapper for city KPI calculation."""
    kpis = calculate_city_kpis(data, city)
    return {
        "avg_rent_latest": kpis["latest_avg_rent"],
        "avg_price_latest": kpis["latest_avg_price"],
        "rent_growth_pct": kpis["rent_growth_pct"],
        "price_growth_pct": kpis["price_growth_pct"],
    }
