"""Backwards-compatible exports for city metrics (legacy Montreal module path)."""

from analysis.city_metrics import (  # noqa: F401
    calculate_city_kpis,
    city_yearly_summary,
    clean_housing_data,
    leader_laggard_summary,
    neighborhood_affordability_snapshot,
    neighborhood_growth_rankings,
    ranking_coverage_summary,
)
