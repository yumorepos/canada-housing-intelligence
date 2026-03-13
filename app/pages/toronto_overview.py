import pandas as pd

from app.pages.city_overview import render_city_overview


CITY_NAME = "Toronto"


def render_toronto_overview(data: pd.DataFrame, profile: dict) -> None:
    render_city_overview(
        data=data,
        city=CITY_NAME,
        subtitle=profile["subtitle"],
        guardrails=profile["guardrails"],
    )
