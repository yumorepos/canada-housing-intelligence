"""Reusable city analysis helpers used by dashboard pages and tests."""

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

    cleaned["borough"] = (
        cleaned["borough"].astype(str).str.strip() if "borough" in cleaned.columns else "Unknown"
    )
    cleaned["property_type"] = (
        cleaned["property_type"].astype(str).str.strip().str.lower() if "property_type" in cleaned.columns else "all"
    )
    cleaned["listing_count"] = (
        pd.to_numeric(cleaned["listing_count"], errors="coerce").fillna(0).astype(int)
        if "listing_count" in cleaned.columns
        else 0
    )
    cleaned["sales_count"] = (
        pd.to_numeric(cleaned["sales_count"], errors="coerce").fillna(0).astype(int)
        if "sales_count" in cleaned.columns
        else 0
    )
    cleaned["coverage_score"] = (
        pd.to_numeric(cleaned["coverage_score"], errors="coerce").fillna(0.6)
        if "coverage_score" in cleaned.columns
        else 0.6
    )
    cleaned["coverage_score"] = cleaned["coverage_score"].clip(lower=0.0, upper=1.0)

    return cleaned.sort_values(["city", "neighborhood", "year"]).reset_index(drop=True)


def city_yearly_summary(data: pd.DataFrame, city: str) -> pd.DataFrame:
    city_data = data[data["city"] == city].copy()
    if "coverage_score" not in city_data.columns:
        city_data["coverage_score"] = 0.6
    if "listing_count" not in city_data.columns:
        city_data["listing_count"] = 0
    if city_data.empty:
        return pd.DataFrame(
            columns=["year", "avg_rent", "avg_price", "rent_to_price_ratio", "avg_coverage_score", "sample_listings"]
        )

    yearly = (
        city_data.groupby("year", as_index=False)
        .agg(
            avg_rent=("average_rent", "mean"),
            avg_price=("median_price", "mean"),
            avg_coverage_score=("coverage_score", "mean"),
            sample_listings=("listing_count", "sum"),
        )
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
                "borough",
                "average_rent",
                "median_price",
                "rent_to_price_ratio",
                "listing_count",
                "coverage_score",
            ]
        )

    latest_year = int(city_data["year"].max())
    snapshot = city_data[city_data["year"] == latest_year].copy()
    snapshot["rent_to_price_ratio"] = (snapshot["average_rent"] * 12) / snapshot["median_price"]

    return snapshot[
        [
            "neighborhood",
            "borough",
            "average_rent",
            "median_price",
            "rent_to_price_ratio",
            "listing_count",
            "coverage_score",
        ]
    ].sort_values("average_rent", ascending=False)


def neighborhood_growth_rankings(
    data: pd.DataFrame,
    city: str,
    min_years: int = 6,
    min_avg_listings: int = 150,
    min_avg_coverage: float = 0.72,
) -> pd.DataFrame:
    city_data = data[data["city"] == city].copy()
    if city_data.empty:
        return pd.DataFrame(
            columns=[
                "neighborhood",
                "borough",
                "rent_growth_pct",
                "price_growth_pct",
                "ratio_change_bps",
                "rent_volatility_pct",
                "price_volatility_pct",
                "years_observed",
                "avg_listings",
                "avg_coverage",
                "support_tier",
                "support_score",
                "reliability_label",
                "is_robust",
            ]
        )

    city_data = city_data.sort_values(["neighborhood", "year"])
    city_data["rent_to_price_ratio"] = (city_data["average_rent"] * 12) / city_data["median_price"]

    growth = city_data.groupby("neighborhood").agg(
        borough=("borough", "first"),
        first_rent=("average_rent", "first"),
        latest_rent=("average_rent", "last"),
        first_price=("median_price", "first"),
        latest_price=("median_price", "last"),
        first_ratio=("rent_to_price_ratio", "first"),
        latest_ratio=("rent_to_price_ratio", "last"),
        years_observed=("year", "nunique"),
        avg_listings=("listing_count", "mean"),
        avg_coverage=("coverage_score", "mean"),
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

    ranked["is_robust"] = (
        (ranked["years_observed"] >= min_years)
        & (ranked["avg_listings"] >= min_avg_listings)
        & (ranked["avg_coverage"] >= min_avg_coverage)
    )
    ranked["support_tier"] = ranked["is_robust"].map({True: "robust", False: "directional"})
    ranked["support_score"] = (
        (ranked["years_observed"] / max(min_years, 1)).clip(upper=1.0) * 40
        + (ranked["avg_listings"] / max(min_avg_listings, 1)).clip(upper=1.0) * 30
        + (ranked["avg_coverage"] / max(min_avg_coverage, 0.01)).clip(upper=1.0) * 30
    ).round(1)
    ranked["reliability_label"] = pd.cut(
        ranked["support_score"],
        bins=[-0.1, 50, 75, 100],
        labels=["low", "medium", "high"],
    ).astype(str)

    return ranked[
        [
            "neighborhood",
            "borough",
            "rent_growth_pct",
            "price_growth_pct",
            "ratio_change_bps",
            "rent_volatility_pct",
            "price_volatility_pct",
            "years_observed",
            "avg_listings",
            "avg_coverage",
            "support_tier",
            "support_score",
            "reliability_label",
            "is_robust",
        ]
    ].sort_values("rent_growth_pct", ascending=False)


def leader_laggard_summary(rankings: pd.DataFrame, metric: str, robust_only: bool = True) -> dict:
    if rankings.empty:
        return {"leader": None, "laggard": None, "scope": "none"}

    scoped = rankings[rankings["is_robust"]].copy() if robust_only else rankings.copy()
    scope = "robust" if robust_only else "all"

    if scoped.empty:
        return {"leader": None, "laggard": None, "scope": "none"}

    sorted_rankings = scoped.sort_values(metric, ascending=False)
    leader = sorted_rankings.iloc[0]
    laggard = sorted_rankings.iloc[-1]

    return {
        "leader": (str(leader["neighborhood"]), float(leader[metric])),
        "laggard": (str(laggard["neighborhood"]), float(laggard[metric])),
        "scope": scope,
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
            "latest_avg_coverage_pct": None,
            "latest_sample_listings": None,
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
        "latest_avg_coverage_pct": float(latest["avg_coverage_score"] * 100),
        "latest_sample_listings": int(latest["sample_listings"]),
    }


def ranking_coverage_summary(rankings: pd.DataFrame) -> dict:
    if rankings.empty:
        return {"total": 0, "robust": 0, "directional": 0}

    robust_count = int(rankings["is_robust"].sum())
    total = int(len(rankings))
    return {"total": total, "robust": robust_count, "directional": total - robust_count}


def canada_city_comparison(data: pd.DataFrame, cities: list[str]) -> pd.DataFrame:
    """Build a city-level comparison table for the Canada overview page."""
    rows = []
    for city in cities:
        kpis = calculate_city_kpis(data, city)
        if kpis["latest_year"] is None:
            continue

        rows.append(
            {
                "city": city,
                "latest_year": kpis["latest_year"],
                "avg_monthly_rent": kpis["latest_avg_rent"],
                "avg_median_price": kpis["latest_avg_price"],
                "rent_growth_pct": kpis["rent_growth_pct"],
                "price_growth_pct": kpis["price_growth_pct"],
                "rent_to_price_ratio_pct": kpis["latest_ratio_pct"],
                "avg_coverage_pct": kpis["latest_avg_coverage_pct"],
                "sample_listings": kpis["latest_sample_listings"],
            }
        )

    comparison = pd.DataFrame(rows)
    if comparison.empty:
        return comparison

    comparison["rent_rank_affordable"] = comparison["avg_monthly_rent"].rank(method="min")
    comparison["price_rank_affordable"] = comparison["avg_median_price"].rank(method="min")
    comparison["pressure_rank"] = (
        (comparison["rent_growth_pct"] + comparison["price_growth_pct"]) / 2
    ).rank(method="min", ascending=False)

    return comparison.sort_values("avg_monthly_rent").reset_index(drop=True)


def canada_comparison_insights(comparison: pd.DataFrame) -> dict:
    """Generate concise decision-oriented insight signals from city comparison data."""
    if comparison.empty:
        return {
            "most_affordable_rent_city": None,
            "most_affordable_price_city": None,
            "highest_pressure_city": None,
            "strongest_coverage_city": None,
            "affordability_gap_rent": None,
            "affordability_gap_price": None,
        }

    lowest_rent = comparison.loc[comparison["avg_monthly_rent"].idxmin()]
    lowest_price = comparison.loc[comparison["avg_median_price"].idxmin()]
    highest_pressure = comparison.assign(
        pressure_score=(comparison["rent_growth_pct"] + comparison["price_growth_pct"]) / 2
    ).sort_values("pressure_score", ascending=False).iloc[0]
    highest_coverage = comparison.loc[comparison["avg_coverage_pct"].idxmax()]

    return {
        "most_affordable_rent_city": str(lowest_rent["city"]),
        "most_affordable_price_city": str(lowest_price["city"]),
        "highest_pressure_city": str(highest_pressure["city"]),
        "strongest_coverage_city": str(highest_coverage["city"]),
        "affordability_gap_rent": float(comparison["avg_monthly_rent"].max() - comparison["avg_monthly_rent"].min()),
        "affordability_gap_price": float(comparison["avg_median_price"].max() - comparison["avg_median_price"].min()),
    }


def canada_multi_city_trends(data: pd.DataFrame, cities: list[str]) -> pd.DataFrame:
    """Return annual trend metrics for supported city-level comparison charts."""
    scoped = data[data["city"].isin(cities)]
    if scoped.empty:
        return pd.DataFrame(columns=["city", "year", "avg_rent", "avg_price", "rent_to_price_ratio"])

    trends = (
        scoped.groupby(["city", "year"], as_index=False)
        .agg(avg_rent=("average_rent", "mean"), avg_price=("median_price", "mean"))
        .sort_values(["city", "year"])
    )
    trends["rent_to_price_ratio"] = (trends["avg_rent"] * 12) / trends["avg_price"]
    return trends
