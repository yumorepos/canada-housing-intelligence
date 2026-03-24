import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import streamlit as st

from analysis.city_metrics import (
    calculate_city_kpis,
    city_yearly_summary,
    leader_laggard_summary,
    neighborhood_affordability_snapshot,
    neighborhood_growth_rankings,
    ranking_coverage_summary,
)


def _format_currency(value: float) -> str:
    return f"${value:,.0f}"


def _leader_caption(summary: dict, label: str) -> str:
    if not summary["leader"] or not summary["laggard"]:
        return f"No robust neighborhoods met the minimum support thresholds for {label.lower()} rankings."
    return (
        f"Top {label.lower()}: **{summary['leader'][0]} ({summary['leader'][1]:.1f}%)**. "
        f"Slowest: **{summary['laggard'][0]} ({summary['laggard'][1]:.1f}%)**."
    )


def render_city_overview(
    data: pd.DataFrame,
    city: str,
    subtitle: str,
    guardrails: dict | None = None,
    provenance: dict | None = None,
) -> None:
    st.header(f"{city} Market Intelligence")
    st.caption(subtitle)
    provenance = provenance or {}

    kpis = calculate_city_kpis(data, city=city)
    yearly = city_yearly_summary(data, city=city)
    snapshot = neighborhood_affordability_snapshot(data, city=city)
    guardrails = guardrails or {}
    rankings = neighborhood_growth_rankings(
        data,
        city=city,
        min_years=int(guardrails.get("min_years", 6)),
        min_avg_listings=int(guardrails.get("min_avg_listings", 150)),
        min_avg_coverage=float(guardrails.get("min_avg_coverage", 0.72)),
    )

    coverage = ranking_coverage_summary(rankings)
    robust_rankings = rankings[rankings["is_robust"]]
    rent_leaders = leader_laggard_summary(rankings, "rent_growth_pct", robust_only=True)
    price_leaders = leader_laggard_summary(rankings, "price_growth_pct", robust_only=True)

    st.subheader("Executive Snapshot")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Avg Monthly Rent", _format_currency(kpis["latest_avg_rent"]), f"{kpis['rent_growth_last_year_pct']:.1f}% YoY")
    c2.metric("Avg Median Sale Price", _format_currency(kpis["latest_avg_price"]), f"{kpis['price_growth_last_year_pct']:.1f}% YoY")
    c3.metric("Rent Growth (period)", f"{kpis['rent_growth_pct']:.1f}%")
    c4.metric("Price Growth (period)", f"{kpis['price_growth_pct']:.1f}%")
    c5.metric("Rent-to-Price Ratio", f"{kpis['latest_ratio_pct']:.2f}%", f"{kpis['ratio_change_bps']:.0f} bps vs start")

    st.info(
        f"**Coverage snapshot ({kpis['latest_year']}):** {kpis['latest_sample_listings']:,} listing observations, "
        f"avg coverage score **{kpis['latest_avg_coverage_pct']:.1f}%**. "
        f"Source: **{provenance.get('source_name', 'local sample dataset')}** ({provenance.get('source_type', 'sample')})."
    )
    st.caption(
        f"Coverage note: {provenance.get('coverage_note', 'Coverage guidance not available.')} · "
        f"Confidence note: {provenance.get('confidence_note', 'Confidence guidance not available.')}"
    )

    st.caption(
        "Neighborhood ranking guardrails: min 6 years, avg listings >= 150, avg coverage >= 0.72. "
        f"Robust neighborhoods: **{coverage['robust']} / {coverage['total']}** (directional: {coverage['directional']})."
    )
    if not rankings.empty:
        avg_support = rankings["support_score"].mean()
        high_support = int((rankings["reliability_label"] == "high").sum())
        st.caption(
            f"Support scoring: mean support score **{avg_support:.1f}/100**; "
            f"high-reliability neighborhoods: **{high_support}/{len(rankings)}**."
        )

    st.subheader("Market Trajectory")
    trend_left, trend_right = st.columns(2)
    with trend_left:
        st.markdown("**Citywide Rent & Price Trend**")
        st.line_chart(yearly, x="year", y=["avg_rent", "avg_price"])
        st.caption("Both rent and sale prices rose through the sample period, with ownership costs rising faster.")

    with trend_right:
        st.markdown("**Affordability Ratio Trend (Annual Rent / Median Price)**")
        st.line_chart(yearly, x="year", y="rent_to_price_ratio")
        st.caption("The ratio trend helps gauge whether rental pressure is easing or tightening versus sale prices.")

    st.subheader("Neighborhood Momentum & Stability (Robust Sample)")
    g1, g2 = st.columns(2)
    with g1:
        st.markdown("**Rent Growth Leaders vs Laggards**")
        if robust_rankings.empty:
            st.warning("No neighborhoods met robustness thresholds for rent growth ranking.")
        else:
            growth_view = robust_rankings[["neighborhood", "rent_growth_pct"]].set_index("neighborhood")
            st.bar_chart(growth_view)
        st.caption(_leader_caption(rent_leaders, "Rent growth"))

    with g2:
        st.markdown("**Price Growth Leaders vs Laggards + Reliability**")
        if robust_rankings.empty:
            st.warning("No neighborhoods met robustness thresholds for price growth ranking.")
        else:
            price_view = robust_rankings[["neighborhood", "price_growth_pct", "support_score"]].set_index("neighborhood")
            st.bar_chart(price_view)
        st.caption(_leader_caption(price_leaders, "Price growth"))

    st.subheader("Current Positioning & Affordability")
    left, right = st.columns([1.3, 1])
    with left:
        st.markdown("**Latest Neighborhood Snapshot**")
        display_snapshot = snapshot.copy()
        display_snapshot["rent_to_price_ratio"] = (display_snapshot["rent_to_price_ratio"] * 100).round(2)
        display_snapshot["coverage_score"] = (display_snapshot["coverage_score"] * 100).round(1)
        display_snapshot = display_snapshot.rename(
            columns={
                "average_rent": "avg_rent",
                "median_price": "median_price",
                "rent_to_price_ratio": "rent_to_price_ratio_pct",
                "listing_count": "listing_obs",
                "coverage_score": "coverage_pct",
            }
        )
        st.dataframe(display_snapshot, use_container_width=True)
        st.caption("Coverage fields indicate how strongly each neighborhood contributes to confidence in local comparisons.")

    with right:
        st.markdown("**Rent vs Price Map (latest year)**")
        st.scatter_chart(snapshot, x="median_price", y="average_rent", color="borough")
        st.caption("Upper-right neighborhoods carry both elevated rents and elevated sale prices.")

    st.subheader("Analyst Notes")
    if robust_rankings.empty:
        st.markdown(
            "- Robust ranking signals are unavailable with current thresholds; use directional values cautiously.\n"
            f"- Latest city sample coverage remains moderate at **{kpis['latest_avg_coverage_pct']:.1f}%**.\n"
            f"- Last processing timestamp: **{provenance.get('processed_at', 'unknown')}**."
        )
    else:
        stable_rent = robust_rankings.sort_values("rent_volatility_pct").iloc[0]
        volatile_rent = robust_rankings.sort_values("rent_volatility_pct", ascending=False).iloc[0]
        avg_support = robust_rankings["support_score"].mean()
        st.markdown(
            "\n".join(
                [
                    f"- **Affordability pressure:** city rent-to-price ratio is **{kpis['latest_ratio_pct']:.2f}%**, "
                    f"a **{kpis['ratio_change_bps']:.0f} bps** move from period start.",
                    f"- **Momentum split (robust sample):** rent growth ranges from **{rent_leaders['laggard'][1]:.1f}%** "
                    f"to **{rent_leaders['leader'][1]:.1f}%**.",
                    f"- **Support confidence:** robust sample mean support score is **{avg_support:.1f}/100**.",
                    f"- **Stability signal:** **{stable_rent['neighborhood']}** is steadiest "
                    f"(volatility {stable_rent['rent_volatility_pct']:.2f}%), while **{volatile_rent['neighborhood']}** is most variable "
                    f"({volatile_rent['rent_volatility_pct']:.2f}%).",
                    f"- **Recency context:** processed at **{provenance.get('processed_at', 'unknown')}**.",
                ]
            )
        )
