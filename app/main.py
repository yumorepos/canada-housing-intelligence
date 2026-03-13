import streamlit as st

from app.pages.montreal_overview import render_montreal_overview
from app.pages.toronto_overview import render_toronto_overview
from app.utils.config import load_city_config
from app.utils.data_loader import load_housing_data


def main() -> None:
    st.set_page_config(page_title="Canada Housing Intelligence", layout="wide")

    st.title("Canada Housing Intelligence")
    st.write(
        "Flagship housing analytics product for Canadian cities. Montreal and Toronto are now implemented city "
        "intelligence views, with Vancouver staged for expansion."
    )

    config = load_city_config()
    cities = config["supported_cities"]

    data = load_housing_data(config["dataset_path"])

    implemented = [name for name, city_cfg in cities.items() if city_cfg["status"] == "live"]
    upcoming = [name for name, city_cfg in cities.items() if city_cfg["status"] != "live"]

    st.caption(f"Implemented cities: **{', '.join(implemented)}**. Upcoming: **{', '.join(upcoming)}**.")

    page_labels = [f"{city} Housing Overview" for city in implemented] + [f"{city} (Coming Soon)" for city in upcoming]
    page = st.sidebar.selectbox("Select city view", page_labels)

    if page == "Montreal Housing Overview":
        render_montreal_overview(data)
    elif page == "Toronto Housing Overview":
        render_toronto_overview(data)
    else:
        st.header("Vancouver")
        st.warning("Vancouver integration is not yet implemented in this local-first sample product.")


if __name__ == "__main__":
    main()
