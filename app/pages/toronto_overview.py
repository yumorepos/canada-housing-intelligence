import pandas as pd

from app.pages.city_overview import render_city_overview

CITY_NAME = "Toronto"


def render_toronto_overview(data: pd.DataFrame) -> None:
    render_city_overview(
        data=data,
        city=CITY_NAME,
        subtitle=(
            "Decision-support view for rental and ownership pressure in Toronto. "
            "Insights are generated from the local sample dataset in this repository."
        ),
    )
