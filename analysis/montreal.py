"""Montreal-focused analysis helpers used by dashboard pages and tests."""

from __future__ import annotations

import pandas as pd

REQUIRED_COLUMNS = {"city", "neighborhood", "year", "average_rent", "median_price"}


def clean_housing_data(data: pd.DataFrame) -> pd.DataFrame:
    """Validate and standardize housing data types for analysis."""
    missing = REQUIRED_COLUMNS.difference(data.columns)
    if missing:
        raise ValueError(f"Dataset is missing required columns: {sorted(missing)}")

    cleaned = data.copy()
    cleaned["city"] = cleaned["city"].astype(str).str.strip()
    cleaned["neighborhood"] = cleaned["neighborhood"].astype(str).str.strip()
    cleaned["year"] = pd.to_numeric(cleaned["year"], errors="raise").astype(int)
    cleaned["average_rent"] = pd.to_numeric(cleaned["average_rent"], errors="raise")
    cleaned["median_price"] = pd.to_numeric(cleaned["median_price"], errors="raise")

    return cleaned.sort_values(["city", "neighborhood", "year"]).reset_index(drop=True)


def city_yearly_summary(data: pd.DataFrame, city: str) -> pd.DataFrame:
    city_data = data[data["city"] == city]
    if city_data.empty:
        return pd.DataFrame(columns=["year", "avg_rent", "avg_price"])

    return (
        city_data.groupby("year", as_index=False)
        .agg(avg_rent=("average_rent", "mean"), avg_price=("median_price", "mean"))
        .sort_values("year")
    )


def neighborhood_affordability_snapshot(data: pd.DataFrame, city: str) -> pd.DataFrame:
    city_data = data[data["city"] == city]
    if city_data.empty:
        return pd.DataFrame(
            columns=[
                "neighborhood",
                "average_rent",
                "median_price",
                "rent_to_price_ratio",
            ]
        )

    latest_year = int(city_data["year"].max())
    snapshot = city_data[city_data["year"] == latest_year].copy()
    snapshot["rent_to_price_ratio"] = (snapshot["average_rent"] * 12) / snapshot["median_price"]

    return snapshot[["neighborhood", "average_rent", "median_price", "rent_to_price_ratio"]].sort_values(
        "average_rent", ascending=False
    )


def calculate_city_kpis(data: pd.DataFrame, city: str) -> dict:
    yearly = city_yearly_summary(data, city)
    if yearly.empty:
        return {
            "latest_avg_rent": None,
            "latest_avg_price": None,
            "rent_growth_pct": None,
            "price_growth_pct": None,
            "latest_year": None,
        }

    first = yearly.iloc[0]
    latest = yearly.iloc[-1]

    rent_growth = ((latest["avg_rent"] - first["avg_rent"]) / first["avg_rent"]) * 100
    price_growth = ((latest["avg_price"] - first["avg_price"]) / first["avg_price"]) * 100

    return {
        "latest_avg_rent": float(latest["avg_rent"]),
        "latest_avg_price": float(latest["avg_price"]),
        "rent_growth_pct": float(rent_growth),
        "price_growth_pct": float(price_growth),
        "latest_year": int(latest["year"]),
    }
