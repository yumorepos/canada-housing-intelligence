import streamlit as st
import pandas as pd

from app.utils.metrics import calculate_housing_metrics


def render_montreal_overview(data: pd.DataFrame) -> None:
    st.header("Montreal Housing Overview")
    st.caption("Starter analytics for affordability and market trends in Montreal neighborhoods.")

    metrics = calculate_housing_metrics(data, city="Montreal")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Avg Rent (Latest Year)", f"${metrics['avg_rent_latest']:,.0f}")
    col2.metric("Median Price (Latest Year)", f"${metrics['avg_price_latest']:,.0f}")
    col3.metric("Rent Growth", f"{metrics['rent_growth_pct']:.1f}%")
    col4.metric("Price Growth", f"{metrics['price_growth_pct']:.1f}%")

    st.subheader("Average Rent Trend")
    city_data = data[data["city"] == "Montreal"].copy()
    trend = (
        city_data.groupby("year", as_index=False)["average_rent"]
        .mean()
        .rename(columns={"average_rent": "avg_rent"})
    )
    st.line_chart(trend, x="year", y="avg_rent")

    st.subheader("Neighborhood Snapshot")
    latest_year = city_data["year"].max()
    latest_view = city_data[city_data["year"] == latest_year].sort_values("average_rent", ascending=False)
    st.dataframe(latest_view, use_container_width=True)
