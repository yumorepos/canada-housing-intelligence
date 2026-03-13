# Canada Housing Intelligence

Canada Housing Intelligence is a portfolio-grade data product foundation for analyzing housing affordability, pricing trends, and livability across major Canadian cities.

The first release focuses on **Montreal**, with architecture intentionally designed to expand to **Toronto** and **Vancouver**.

## Motivation
Canada's housing market is complex and rapidly evolving. This project is built to answer practical questions such as:
- How fast are rents and home prices changing?
- Which neighborhoods show the strongest affordability pressure?
- How can we compare housing conditions across cities using consistent metrics?

This repository establishes a clean base for future analytics pipelines, machine learning models, and richer city-level insights.

## Planned Architecture
```text
app/                Streamlit dashboard app
  pages/            City-specific dashboard modules
analysis/           Metric definitions and analytical notebooks/scripts
etl/                Data ingestion and transformation jobs
data/
  raw/              Source data dumps
  processed/        Cleaned and model-ready datasets
models/             Predictive modeling code and artifacts
tests/              Unit and integration tests
config/             City and dataset configuration
```

## Current Features (Initial Foundation)
- Streamlit dashboard branded as **Canada Housing Intelligence**
- Montreal Housing Overview page with:
  - Starter KPIs (latest average rent and median home price)
  - Rent and price growth metrics
  - Rent trend visualization
  - Neighborhood snapshot table
- Local sample dataset (`data/processed/housing_sample.csv`) to run without external APIs
- City configuration file for Montreal, Toronto, and Vancouver roadmap support

## Future Roadmap
### Phase 1 (Current)
- Montreal baseline analytics and dashboard scaffolding

### Phase 2
- Add Toronto and Vancouver datasets
- Introduce city comparison views
- Build affordability scoring framework

### Phase 3
- ETL automation for public housing data sources
- Predictive models for rent and price trends
- Geospatial visualizations for neighborhood-level insights

## Tech Stack
- **Python 3.10+**
- **Streamlit** for the interactive dashboard
- **Pandas** for data manipulation and metrics
- **YAML config** for city and dataset settings

## Run Locally
1. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Launch the dashboard:
   ```bash
   streamlit run app/main.py
   ```

## Project Direction
This codebase intentionally avoids overengineering while keeping a production-minded structure. The current implementation is simple, local, and runnable, but organized for straightforward expansion into a full housing intelligence platform.
