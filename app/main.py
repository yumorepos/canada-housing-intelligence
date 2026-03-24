from datetime import UTC, datetime
import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from app.pages.canada_overview import render_canada_overview
from app.utils.config import get_city_profiles, get_profiled_cities, load_city_config
from app.utils.data_loader import load_housing_dataset


def _render_data_mode_banner(provenance: dict, max_age_days: int = 45) -> None:
    data_mode = provenance.get("data_mode", "sample")
    label = "Source-backed processed" if data_mode == "source_backed" else "Local sample"
    st.caption(
        f"**Data mode:** {label} · **Source:** {provenance.get('source_name', 'unknown')} "
        f"({provenance.get('source_type', 'unknown')}) · **Period:** {provenance.get('source_period', 'unknown')}"
    )
    processed_at_raw = provenance.get("processed_at")
    if not processed_at_raw or processed_at_raw == "unknown":
        st.warning("Freshness status unavailable: no processed_at timestamp found in current dataset.")
        return

    try:
        processed_at = datetime.fromisoformat(str(processed_at_raw).replace("Z", "+00:00"))
        if processed_at.tzinfo is None:
            processed_at = processed_at.replace(tzinfo=UTC)
        age_days = (datetime.now(UTC) - processed_at).days
    except ValueError:
        st.warning(f"Freshness status unavailable: invalid processed_at format ({processed_at_raw}).")
        return

    if age_days > max_age_days:
        st.warning(
            f"Data freshness: stale ({age_days} days old). Threshold is {max_age_days} days."
        )
    else:
        st.caption(f"Data freshness: {age_days} days old (threshold: {max_age_days} days).")


def _resolve_city_renderer(city: str):
    module_name = f"app.pages.{city.lower()}_overview"
    function_name = f"render_{city.lower()}_overview"
    try:
        module = importlib.import_module(module_name)
    except ModuleNotFoundError:
        return None
    return getattr(module, function_name, None)


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

    freshness_max_age_days = int(defaults.get("freshness", {}).get("max_age_days", 45))
    _render_data_mode_banner(provenance, max_age_days=freshness_max_age_days)

    st.caption(
        f"Implemented cities: **{', '.join(implemented_names)}**. "
        f"Upcoming: **{', '.join(upcoming_names) if upcoming_names else 'None'}**."
    )

    page_labels = ["Canada Overview"] + [f"{city} Housing Overview" for city in implemented_names] + [
        f"{city} (Coming Soon)" for city in upcoming_names
    ]
    page = st.sidebar.selectbox("Select experience", page_labels)

    if page == "Canada Overview":
        render_canada_overview(
            data,
            implemented_profiles=implemented_profiles,
            upcoming_profiles=upcoming_profiles,
            provenance=provenance,
        )
    elif page.endswith("Housing Overview"):
        city = page.replace(" Housing Overview", "")
        renderer = _resolve_city_renderer(city)
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
