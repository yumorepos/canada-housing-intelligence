import pandas as pd
import streamlit as st

from analysis.montreal import (
    calculate_city_kpis,
    city_yearly_summary,
    leader_laggard_summary,
    neighborhood_affordability_snapshot,
    neighborhood_growth_rankings,
)


CITY_NAME = "Montreal"


def _format_currency(value: float) -> str:
    return f"${value:,.0f}"


def render_montreal_overview(data: pd.DataFrame) -> None:
    st.header("Montreal Market Intelligence")
    st.caption(
        "Decision-support view for rental and ownership pressure in Montreal. "
        "Insights are generated from the local sample dataset in this repository."
    )

    kpis = calculate_city_kpis(data, city=CITY_NAME)
    yearly = city_yearly_summary(data, city=CITY_NAME)
    snapshot = neighborhood_affordability_snapshot(data, city=CITY_NAME)
    rankings = neighborhood_growth_rankings(data, city=CITY_NAME)

    rent_leaders = leader_laggard_summary(rankings, "rent_growth_pct")
    price_leaders = leader_laggard_summary(rankings, "price_growth_pct")

    st.subheader("Executive Snapshot")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Avg Monthly Rent", _format_currency(kpis["latest_avg_rent"]), f"{kpis['rent_growth_last_year_pct']:.1f}% YoY")
    c2.metric("Avg Median Sale Price", _format_currency(kpis["latest_avg_price"]), f"{kpis['price_growth_last_year_pct']:.1f}% YoY")
    c3.metric("Rent Growth (period)", f"{kpis['rent_growth_pct']:.1f}%")
    c4.metric("Price Growth (period)", f"{kpis['price_growth_pct']:.1f}%")
    c5.metric("Rent-to-Price Ratio", f"{kpis['latest_ratio_pct']:.2f}%", f"{kpis['ratio_change_bps']:.0f} bps vs start")

    st.info(
        f"**Year covered:** {int(yearly['year'].min())}-{kpis['latest_year']}. "
        "This is a directional market sample, not an official citywide benchmark."
    )

    st.subheader("Market Trajectory")
    trend_left, trend_right = st.columns(2)
    with trend_left:
        st.markdown("**Citywide Rent & Price Trend**")
        st.line_chart(yearly, x="year", y=["avg_rent", "avg_price"])
        st.caption("Both rent and sale prices have moved upward across the sample period, with price growth slightly ahead.")

    with trend_right:
        st.markdown("**Affordability Ratio Trend (Annual Rent / Median Price)**")
        st.line_chart(yearly, x="year", y="rent_to_price_ratio")
        st.caption("A stable-to-rising ratio suggests rental pressure has not meaningfully eased relative to ownership costs.")

    st.subheader("Neighborhood Momentum & Stability")
    g1, g2 = st.columns(2)
    with g1:
        st.markdown("**Rent Growth Leaders vs Laggards**")
        growth_view = rankings[["neighborhood", "rent_growth_pct"]].set_index("neighborhood")
        st.bar_chart(growth_view)
        st.caption(
            f"Top rent acceleration: **{rent_leaders['leader'][0]} ({rent_leaders['leader'][1]:.1f}%)**. "
            f"Slowest: **{rent_leaders['laggard'][0]} ({rent_leaders['laggard'][1]:.1f}%)**."
        )

    with g2:
        st.markdown("**Price Growth Leaders vs Laggards**")
        price_view = rankings[["neighborhood", "price_growth_pct"]].set_index("neighborhood")
        st.bar_chart(price_view)
        st.caption(
            f"Top sale-price growth: **{price_leaders['leader'][0]} ({price_leaders['leader'][1]:.1f}%)**. "
            f"Slowest: **{price_leaders['laggard'][0]} ({price_leaders['laggard'][1]:.1f}%)**."
        )

    st.subheader("Current Positioning & Affordability")
    left, right = st.columns([1.2, 1])
    with left:
        st.markdown("**Latest Neighborhood Snapshot**")
        display_snapshot = snapshot.copy()
        display_snapshot["rent_to_price_ratio"] = (display_snapshot["rent_to_price_ratio"] * 100).round(2)
        display_snapshot = display_snapshot.rename(
            columns={
                "average_rent": "avg_rent",
                "median_price": "median_price",
                "rent_to_price_ratio": "rent_to_price_ratio_pct",
            }
        )
        st.dataframe(display_snapshot, use_container_width=True)
        st.caption("Higher rent-to-price ratios can indicate comparatively stronger rental yield-like pressure.")

    with right:
        st.markdown("**Rent vs Price Map (latest year)**")
        st.scatter_chart(snapshot, x="median_price", y="average_rent", color="neighborhood")
        st.caption("Upper-right neighborhoods carry both elevated rents and elevated sale prices.")

    st.subheader("Analyst Notes")
    stable_rent = rankings.sort_values("rent_volatility_pct").iloc[0]
    volatile_rent = rankings.sort_values("rent_volatility_pct", ascending=False).iloc[0]
    st.markdown(
        "\n".join(
            [
                f"- **Affordability pressure:** The city-level rent-to-price ratio sits at **{kpis['latest_ratio_pct']:.2f}%**, "
                f"a **{kpis['ratio_change_bps']:.0f} bps** change versus the start of the sample.",
                f"- **Momentum split:** Rent growth spans from **{rent_leaders['laggard'][1]:.1f}%** "
                f"to **{rent_leaders['leader'][1]:.1f}%** across neighborhoods, showing uneven acceleration.",
                f"- **Stability signal:** **{stable_rent['neighborhood']}** shows the steadiest rent path "
                f"(volatility {stable_rent['rent_volatility_pct']:.2f}%), while **{volatile_rent['neighborhood']}** is the most variable "
                f"({volatile_rent['rent_volatility_pct']:.2f}%).",
            ]
        )
    )
