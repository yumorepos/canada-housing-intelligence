import streamlit as st

from app.pages.montreal_overview import render_montreal_overview
from app.utils.config import load_city_config
from app.utils.data_loader import load_housing_data


def main() -> None:
    st.set_page_config(page_title="Canada Housing Intelligence", layout="wide")

    st.title("Canada Housing Intelligence")
    st.write(
        "A local-first housing analytics platform focused on affordability, market pricing, "
        "and livability insights across major Canadian cities."
    )

    config = load_city_config()
    data = load_housing_data(config["data"]["default_dataset_path"])

    page = st.sidebar.selectbox(
        "Select dashboard view",
        ["Montreal Housing Overview", "Toronto (Coming Soon)", "Vancouver (Coming Soon)"],
    )

    if page == "Montreal Housing Overview":
        render_montreal_overview(data)
    elif page == "Toronto (Coming Soon)":
        st.header("Toronto Dashboard")
        st.info("Toronto analytics modules will be added in upcoming iterations.")
    else:
        st.header("Vancouver Dashboard")
        st.info("Vancouver analytics modules will be added in upcoming iterations.")


if __name__ == "__main__":
    main()
