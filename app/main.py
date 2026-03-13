import streamlit as st

from app.pages.montreal_overview import render_montreal_overview
from app.utils.config import load_city_config
from app.utils.data_loader import load_housing_data


def main() -> None:
    st.set_page_config(page_title="Canada Housing Intelligence", layout="wide")

    st.title("Canada Housing Intelligence")
    st.write(
        "Flagship housing analytics product for Canadian cities. Montreal is now the first implemented city case study, "
        "with Toronto and Vancouver staged for expansion."
    )

    config = load_city_config()
    cities = config["supported_cities"]
    montreal_cfg = cities["Montreal"]
    data = load_housing_data(montreal_cfg["dataset_path"])

    page = st.sidebar.selectbox(
        "Select city view",
        ["Montreal Housing Overview", "Toronto (Coming Soon)", "Vancouver (Coming Soon)"],
    )

    if page == "Montreal Housing Overview":
        render_montreal_overview(data)
    elif page == "Toronto (Coming Soon)":
        st.header("Toronto")
        st.warning("Toronto integration is not yet migrated into this flagship repo.")
    else:
        st.header("Vancouver")
        st.warning("Vancouver integration is not yet migrated into this flagship repo.")


if __name__ == "__main__":
    main()
