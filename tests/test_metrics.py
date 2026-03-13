import pandas as pd

from analysis.city_metrics import (
    calculate_city_kpis,
    canada_city_comparison,
    canada_comparison_insights,
    canada_multi_city_trends,
    clean_housing_data,
    leader_laggard_summary,
    neighborhood_affordability_snapshot,
    neighborhood_growth_rankings,
    ranking_coverage_summary,
)
from app.utils.metrics import calculate_housing_metrics


def test_clean_housing_data_standardizes_and_sorts_with_defaults():
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
    assert cleaned.loc[0, "coverage_score"] == 0.6
    assert cleaned.loc[0, "listing_count"] == 0


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


def test_affordability_snapshot_adds_ratio_and_coverage_columns():
    df = pd.DataFrame(
        {
            "city": ["Montreal", "Montreal"],
            "neighborhood": ["A", "B"],
            "borough": ["X", "Y"],
            "year": [2023, 2023],
            "average_rent": [1200, 1800],
            "median_price": [400000, 600000],
            "listing_count": [100, 120],
            "coverage_score": [0.7, 0.9],
        }
    )

    snapshot = neighborhood_affordability_snapshot(df, "Montreal")

    assert "rent_to_price_ratio" in snapshot.columns
    assert "coverage_score" in snapshot.columns
    assert snapshot.iloc[0]["average_rent"] == 1800


def test_calculate_city_kpis_returns_coverage_fields():
    df = pd.DataFrame(
        {
            "city": ["Montreal", "Montreal", "Montreal"],
            "neighborhood": ["A", "A", "A"],
            "year": [2021, 2022, 2023],
            "average_rent": [1000, 1100, 1200],
            "median_price": [400000, 420000, 450000],
            "listing_count": [100, 110, 120],
            "coverage_score": [0.7, 0.8, 0.9],
        }
    )

    kpis = calculate_city_kpis(df, "Montreal")

    assert kpis["latest_year"] == 2023
    assert kpis["latest_ratio_pct"] is not None
    assert kpis["rent_growth_last_year_pct"] > 0
    assert kpis["latest_avg_coverage_pct"] == 90.0
    assert kpis["latest_sample_listings"] == 120


def test_neighborhood_growth_rankings_respect_robustness_thresholds():
    df = pd.DataFrame(
        {
            "city": ["Montreal"] * 12,
            "neighborhood": ["A"] * 6 + ["B"] * 6,
            "borough": ["X"] * 6 + ["Y"] * 6,
            "year": [2019, 2020, 2021, 2022, 2023, 2024] * 2,
            "average_rent": [1000, 1050, 1100, 1160, 1210, 1270, 1000, 1010, 1020, 1030, 1040, 1050],
            "median_price": [400000, 415000, 430000, 445000, 462000, 480000, 400000, 405000, 410000, 415000, 420000, 425000],
            "listing_count": [220, 210, 205, 215, 225, 230, 80, 90, 85, 88, 92, 95],
            "coverage_score": [0.85, 0.86, 0.87, 0.88, 0.86, 0.87, 0.60, 0.62, 0.61, 0.63, 0.62, 0.64],
        }
    )

    rankings = neighborhood_growth_rankings(df, "Montreal")
    summary = leader_laggard_summary(rankings, "rent_growth_pct", robust_only=True)
    coverage_summary = ranking_coverage_summary(rankings)

    assert set(["support_tier", "is_robust", "avg_coverage"]).issubset(rankings.columns)
    assert rankings.loc[rankings["neighborhood"] == "A", "is_robust"].iloc[0]
    assert not rankings.loc[rankings["neighborhood"] == "B", "is_robust"].iloc[0]
    assert summary["leader"][0] == "A"
    assert summary["laggard"][0] == "A"
    assert coverage_summary == {"total": 2, "robust": 1, "directional": 1}


def test_multi_city_logic_keeps_city_scopes_independent():
    df = pd.DataFrame(
        {
            "city": ["Montreal", "Montreal", "Toronto", "Toronto"],
            "neighborhood": ["A", "A", "A", "A"],
            "borough": ["X", "X", "Y", "Y"],
            "year": [2023, 2024, 2023, 2024],
            "average_rent": [1400, 1500, 2200, 2300],
            "median_price": [500000, 525000, 800000, 840000],
            "listing_count": [200, 210, 260, 270],
            "coverage_score": [0.8, 0.82, 0.9, 0.91],
        }
    )

    montreal_kpis = calculate_city_kpis(df, "Montreal")
    toronto_kpis = calculate_city_kpis(df, "Toronto")

    assert montreal_kpis["latest_avg_rent"] == 1500
    assert toronto_kpis["latest_avg_rent"] == 2300
    assert toronto_kpis["latest_avg_price"] > montreal_kpis["latest_avg_price"]


def test_canada_city_comparison_returns_decision_fields():
    df = pd.DataFrame(
        {
            "city": ["Montreal", "Montreal", "Toronto", "Toronto"],
            "neighborhood": ["A", "A", "A", "A"],
            "year": [2023, 2024, 2023, 2024],
            "average_rent": [1500, 1600, 2300, 2400],
            "median_price": [550000, 575000, 850000, 890000],
            "listing_count": [200, 210, 300, 320],
            "coverage_score": [0.8, 0.82, 0.9, 0.91],
        }
    )

    comparison = canada_city_comparison(df, ["Montreal", "Toronto"])

    assert list(comparison["city"]) == ["Montreal", "Toronto"]
    assert set(["rent_rank_affordable", "price_rank_affordable", "pressure_rank"]).issubset(comparison.columns)
    assert comparison.loc[comparison["city"] == "Montreal", "rent_rank_affordable"].iloc[0] == 1


def test_canada_comparison_insights_identify_tradeoffs():
    comparison = pd.DataFrame(
        {
            "city": ["Montreal", "Toronto"],
            "avg_monthly_rent": [1600.0, 2400.0],
            "avg_median_price": [575000.0, 890000.0],
            "rent_growth_pct": [8.0, 12.0],
            "price_growth_pct": [10.0, 14.0],
            "avg_coverage_pct": [82.0, 91.0],
        }
    )

    insights = canada_comparison_insights(comparison)

    assert insights["most_affordable_rent_city"] == "Montreal"
    assert insights["highest_pressure_city"] == "Toronto"
    assert insights["affordability_gap_rent"] == 800.0


def test_canada_multi_city_trends_builds_city_year_series():
    df = pd.DataFrame(
        {
            "city": ["Montreal", "Montreal", "Toronto", "Toronto", "Calgary"],
            "neighborhood": ["A", "A", "A", "A", "A"],
            "year": [2023, 2024, 2023, 2024, 2024],
            "average_rent": [1500, 1600, 2300, 2400, 1800],
            "median_price": [550000, 575000, 850000, 890000, 700000],
        }
    )

    trends = canada_multi_city_trends(df, ["Montreal", "Toronto"])

    assert set(trends["city"]) == {"Montreal", "Toronto"}
    assert "rent_to_price_ratio" in trends.columns
    assert len(trends) == 4


def test_sample_dataset_includes_vancouver_with_multi_year_coverage():
    df = pd.read_csv("data/processed/housing_sample.csv")

    vancouver = df[df["city"] == "Vancouver"]
    assert not vancouver.empty
    assert vancouver["year"].nunique() >= 6
    assert vancouver["neighborhood"].nunique() >= 6
    assert set(["listing_count", "coverage_score"]).issubset(vancouver.columns)


def test_canada_city_comparison_supports_three_live_cities():
    df = pd.read_csv("data/processed/housing_sample.csv")

    comparison = canada_city_comparison(df, ["Montreal", "Toronto", "Vancouver"])

    assert set(comparison["city"]) == {"Montreal", "Toronto", "Vancouver"}
    assert comparison["city"].nunique() == 3
    assert comparison["sample_listings"].min() > 0
