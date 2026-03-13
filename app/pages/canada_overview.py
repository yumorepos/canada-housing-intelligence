import pandas as pd
import streamlit as st

from analysis.city_metrics import canada_city_comparison, canada_comparison_insights, canada_multi_city_trends


def _currency(value: float) -> str:
    return f"${value:,.0f}"


def render_canada_overview(data: pd.DataFrame, implemented_cities: list[str], upcoming_cities: list[str]) -> None:
    st.header("Canada Market Comparison")
    st.caption(
        "National comparison layer for currently implemented cities. Values are based on the local/sample "
        "dataset shipped with this repository and should be treated as directional intelligence."
    )

    comparison = canada_city_comparison(data, implemented_cities)
    insights = canada_comparison_insights(comparison)
    trends = canada_multi_city_trends(data, implemented_cities)

    if comparison.empty:
        st.warning("No live city data is currently available for Canada-level comparison.")
        return

    st.subheader("Decision Snapshot")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Lower Rent City", insights["most_affordable_rent_city"], _currency(insights["affordability_gap_rent"]))
    c2.metric("Lower Price City", insights["most_affordable_price_city"], _currency(insights["affordability_gap_price"]))
    c3.metric("Higher Pressure City", insights["highest_pressure_city"])
    c4.metric("Best Data Coverage", insights["strongest_coverage_city"])

    st.info(
        f"Live comparisons currently cover **{', '.join(implemented_cities)}**. "
        f"Upcoming cities: **{', '.join(upcoming_cities)}**."
    )

    st.subheader("City Comparison Table")
    table = comparison[
        [
            "city",
            "latest_year",
            "avg_monthly_rent",
            "avg_median_price",
            "rent_growth_pct",
            "price_growth_pct",
            "rent_to_price_ratio_pct",
            "avg_coverage_pct",
            "sample_listings",
        ]
    ].copy()
    table = table.rename(
        columns={
            "city": "City",
            "latest_year": "Latest Year",
            "avg_monthly_rent": "Avg Monthly Rent",
            "avg_median_price": "Avg Median Price",
            "rent_growth_pct": "Rent Growth %",
            "price_growth_pct": "Price Growth %",
            "rent_to_price_ratio_pct": "Rent-to-Price Ratio %",
            "avg_coverage_pct": "Coverage %",
            "sample_listings": "Listing Samples",
        }
    )

    st.dataframe(
        table.style.format(
            {
                "Avg Monthly Rent": "${:,.0f}",
                "Avg Median Price": "${:,.0f}",
                "Rent Growth %": "{:.1f}",
                "Price Growth %": "{:.1f}",
                "Rent-to-Price Ratio %": "{:.2f}",
                "Coverage %": "{:.1f}",
                "Listing Samples": "{:,.0f}",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Cross-City Trends")
    left, right = st.columns(2)
    with left:
        st.markdown("**Affordability Now: Rent vs Price by City**")
        st.bar_chart(comparison.set_index("city")[["avg_monthly_rent", "avg_median_price"]])
        st.caption("Shows absolute cost tradeoffs: monthly rental burden versus ownership entry price.")

    with right:
        st.markdown("**Market Pressure: Rent Growth vs Price Growth**")
        st.bar_chart(comparison.set_index("city")[["rent_growth_pct", "price_growth_pct"]])
        st.caption("Highlights where pressure has been stronger over the sample period.")

    st.markdown("**Trend Divergence Over Time: Rent-to-Price Ratio**")
    st.line_chart(trends, x="year", y="rent_to_price_ratio", color="city")

    st.subheader("Analyst Notes")
    st.markdown(
        "- **Affordability tradeoff:** Lower current rent and lower median purchase price are not always paired with weaker growth; "
        "this view helps make that tradeoff explicit.\n"
        "- **Pressure signal:** We define pressure as combined rent and price growth over time to show where household cost stress "
        "is building faster.\n"
        "- **Honest scope:** This is a local/sample intelligence layer with support and coverage guardrails, not an authoritative "
        "national benchmark feed."
    )
