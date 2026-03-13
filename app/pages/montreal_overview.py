import pandas as pd
import streamlit as st

from analysis.montreal import (
    calculate_city_kpis,
    city_yearly_summary,
    neighborhood_affordability_snapshot,
)


def render_montreal_overview(data: pd.DataFrame) -> None:
    st.header("Montreal Housing Intelligence")
    st.caption(
        "Production-ready first city view: track price pressure, rent acceleration, and neighborhood affordability patterns."
    )

    kpis = calculate_city_kpis(data, city="Montreal")
    yearly = city_yearly_summary(data, city="Montreal")
    snapshot = neighborhood_affordability_snapshot(data, city="Montreal")

    st.subheader("Market KPIs")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Latest Avg Rent", f"${kpis['latest_avg_rent']:,.0f}")
    c2.metric("Latest Median Price", f"${kpis['latest_avg_price']:,.0f}")
    c3.metric("Rent Growth Since Start", f"{kpis['rent_growth_pct']:.1f}%")
    c4.metric("Price Growth Since Start", f"{kpis['price_growth_pct']:.1f}%")

    left, right = st.columns(2)
    with left:
        st.subheader("Citywide Rent Trend")
        st.line_chart(yearly, x="year", y="avg_rent")
    with right:
        st.subheader("Citywide Median Price Trend")
        st.line_chart(yearly, x="year", y="avg_price")

    st.subheader("Neighborhood Affordability Snapshot")
    st.write(
        f"Latest year in dataset: **{kpis['latest_year']}**. `rent_to_price_ratio` is annual rent divided by median price."
    )
    st.dataframe(snapshot, use_container_width=True)

    st.subheader("Rent vs Price Positioning")
    st.scatter_chart(snapshot, x="median_price", y="average_rent", color="neighborhood")

    st.info(
        "Interpretation: neighborhoods in the upper-right have both high rents and high sale prices, "
        "while high rent-to-price ratios can indicate stronger yield-like rental pressure."
    )
