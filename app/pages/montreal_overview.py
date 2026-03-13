import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd

from app.pages.city_overview import render_city_overview


CITY_NAME = "Montreal"


def render_montreal_overview(data: pd.DataFrame, profile: dict, provenance: dict | None = None) -> None:
    render_city_overview(
        data=data,
        city=CITY_NAME,
        subtitle=profile["subtitle"],
        guardrails=profile["guardrails"],
        provenance=provenance,
    )
