import pandas as pd


def calculate_housing_metrics(data: pd.DataFrame, city: str) -> dict:
    """Calculate starter housing KPIs for a city."""
    city_data = data[data["city"] == city]
    if city_data.empty:
        return {
            "avg_rent_latest": None,
            "avg_price_latest": None,
            "rent_growth_pct": None,
            "price_growth_pct": None,
        }

    latest_year = city_data["year"].max()
    first_year = city_data["year"].min()

    latest = city_data[city_data["year"] == latest_year]
    first = city_data[city_data["year"] == first_year]

    avg_rent_latest = latest["average_rent"].mean()
    avg_price_latest = latest["median_price"].mean()
    avg_rent_first = first["average_rent"].mean()
    avg_price_first = first["median_price"].mean()

    rent_growth_pct = ((avg_rent_latest - avg_rent_first) / avg_rent_first) * 100
    price_growth_pct = ((avg_price_latest - avg_price_first) / avg_price_first) * 100

    return {
        "avg_rent_latest": avg_rent_latest,
        "avg_price_latest": avg_price_latest,
        "rent_growth_pct": rent_growth_pct,
        "price_growth_pct": price_growth_pct,
    }
