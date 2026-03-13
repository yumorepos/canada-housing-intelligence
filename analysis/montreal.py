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
        return pd.DataFrame(columns=["year", "avg_rent", "avg_price", "rent_to_price_ratio"])

    yearly = (
        city_data.groupby("year", as_index=False)
        .agg(avg_rent=("average_rent", "mean"), avg_price=("median_price", "mean"))
        .sort_values("year")
    )
    yearly["rent_to_price_ratio"] = (yearly["avg_rent"] * 12) / yearly["avg_price"]
    yearly["rent_growth_yoy_pct"] = yearly["avg_rent"].pct_change() * 100
    yearly["price_growth_yoy_pct"] = yearly["avg_price"].pct_change() * 100

    return yearly


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


def neighborhood_growth_rankings(data: pd.DataFrame, city: str) -> pd.DataFrame:
    city_data = data[data["city"] == city].copy()
    if city_data.empty:
        return pd.DataFrame(
            columns=[
                "neighborhood",
                "rent_growth_pct",
                "price_growth_pct",
                "ratio_change_bps",
                "rent_volatility_pct",
                "price_volatility_pct",
            ]
        )

    city_data = city_data.sort_values(["neighborhood", "year"])
    city_data["rent_to_price_ratio"] = (city_data["average_rent"] * 12) / city_data["median_price"]

    growth = city_data.groupby("neighborhood").agg(
        first_rent=("average_rent", "first"),
        latest_rent=("average_rent", "last"),
        first_price=("median_price", "first"),
        latest_price=("median_price", "last"),
        first_ratio=("rent_to_price_ratio", "first"),
        latest_ratio=("rent_to_price_ratio", "last"),
    )

    city_data["rent_growth_yoy_pct"] = city_data.groupby("neighborhood")["average_rent"].pct_change() * 100
    city_data["price_growth_yoy_pct"] = city_data.groupby("neighborhood")["median_price"].pct_change() * 100
    volatility = city_data.groupby("neighborhood").agg(
        rent_volatility_pct=("rent_growth_yoy_pct", "std"),
        price_volatility_pct=("price_growth_yoy_pct", "std"),
    )

    ranked = growth.join(volatility).reset_index()
    ranked["rent_growth_pct"] = ((ranked["latest_rent"] - ranked["first_rent"]) / ranked["first_rent"]) * 100
    ranked["price_growth_pct"] = ((ranked["latest_price"] - ranked["first_price"]) / ranked["first_price"]) * 100
    ranked["ratio_change_bps"] = (ranked["latest_ratio"] - ranked["first_ratio"]) * 10000

    return ranked[
        [
            "neighborhood",
            "rent_growth_pct",
            "price_growth_pct",
            "ratio_change_bps",
            "rent_volatility_pct",
            "price_volatility_pct",
        ]
    ].sort_values("rent_growth_pct", ascending=False)


def leader_laggard_summary(rankings: pd.DataFrame, metric: str) -> dict:
    if rankings.empty:
        return {"leader": None, "laggard": None}

    sorted_rankings = rankings.sort_values(metric, ascending=False)
    leader = sorted_rankings.iloc[0]
    laggard = sorted_rankings.iloc[-1]

    return {
        "leader": (str(leader["neighborhood"]), float(leader[metric])),
        "laggard": (str(laggard["neighborhood"]), float(laggard[metric])),
    }


def calculate_city_kpis(data: pd.DataFrame, city: str) -> dict:
    yearly = city_yearly_summary(data, city)
    if yearly.empty:
        return {
            "latest_avg_rent": None,
            "latest_avg_price": None,
            "rent_growth_pct": None,
            "price_growth_pct": None,
            "latest_year": None,
            "latest_ratio_pct": None,
            "ratio_change_bps": None,
            "rent_growth_last_year_pct": None,
            "price_growth_last_year_pct": None,
        }

    first = yearly.iloc[0]
    latest = yearly.iloc[-1]

    rent_growth = ((latest["avg_rent"] - first["avg_rent"]) / first["avg_rent"]) * 100
    price_growth = ((latest["avg_price"] - first["avg_price"]) / first["avg_price"]) * 100
    ratio_change_bps = (latest["rent_to_price_ratio"] - first["rent_to_price_ratio"]) * 10000

    return {
        "latest_avg_rent": float(latest["avg_rent"]),
        "latest_avg_price": float(latest["avg_price"]),
        "rent_growth_pct": float(rent_growth),
        "price_growth_pct": float(price_growth),
        "latest_year": int(latest["year"]),
        "latest_ratio_pct": float(latest["rent_to_price_ratio"] * 100),
        "ratio_change_bps": float(ratio_change_bps),
        "rent_growth_last_year_pct": float(latest["rent_growth_yoy_pct"]),
        "price_growth_last_year_pct": float(latest["price_growth_yoy_pct"]),
    }
