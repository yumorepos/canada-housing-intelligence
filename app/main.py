import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from app.pages.canada_overview import render_canada_overview
from app.pages.montreal_overview import render_montreal_overview
from app.pages.toronto_overview import render_toronto_overview
from app.pages.vancouver_overview import render_vancouver_overview
from app.utils.config import get_city_profiles, get_profiled_cities, load_city_config
from app.utils.data_loader import load_housing_dataset


def _render_data_mode_banner(provenance: dict) -> None:
    data_mode = provenance.get("data_mode", "sample")
    label = "Source-backed processed" if data_mode == "source_backed" else "Local sample"
    st.caption(
        f"**Data mode:** {label} · **Source:** {provenance.get('source_name', 'unknown')} "
        f"({provenance.get('source_type', 'unknown')}) · **Period:** {provenance.get('source_period', 'unknown')}"
    )


def main() -> None:
    st.set_page_config(page_title="Canada Housing Intelligence", layout="wide")

    st.title("Canada Housing Intelligence")
    st.write(
        "National housing intelligence product for Canadian cities. Start with Canada-wide comparison, "
        "then drill into implemented city intelligence views."
    )

    config = load_city_config()
    profiles = get_city_profiles(config)
    implemented_profiles, upcoming_profiles = get_profiled_cities(config)

    defaults = config["shared_defaults"]
    data, provenance = load_housing_dataset(
        dataset_path=defaults["dataset_path"],
        fallback_path=defaults["fallback_dataset_path"],
    )

    implemented_names = [profile["city"] for profile in implemented_profiles]
    upcoming_names = [profile["city"] for profile in upcoming_profiles]

    _render_data_mode_banner(provenance)

    st.caption(
        f"Implemented cities: **{', '.join(implemented_names)}**. "
        f"Upcoming: **{', '.join(upcoming_names) if upcoming_names else 'None'}**."
    )

    page_labels = ["Canada Overview"] + [f"{city} Housing Overview" for city in implemented_names] + [
        f"{city} (Coming Soon)" for city in upcoming_names
    ]
    page = st.sidebar.selectbox("Select experience", page_labels)

    city_renderers = {
        "Montreal": render_montreal_overview,
        "Toronto": render_toronto_overview,
        "Vancouver": render_vancouver_overview,
    }

    if page == "Canada Overview":
        render_canada_overview(
            data,
            implemented_profiles=implemented_profiles,
            upcoming_profiles=upcoming_profiles,
            provenance=provenance,
        )
    elif page.endswith("Housing Overview"):
        city = page.replace(" Housing Overview", "")
        renderer = city_renderers.get(city)
        if renderer and city in profiles:
            renderer(data, profile=profiles[city], provenance=provenance)
        else:
            st.error(f"No renderer configured for {city}.")
    else:
        city = page.replace(" (Coming Soon)", "")
        note = profiles.get(city, {}).get("upcoming_note")
        st.header(city)
        st.warning(note or "This city is not yet implemented in this local-first sample product.")


if __name__ == "__main__":
    main()
