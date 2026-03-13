# Canada Housing Intelligence

Canada Housing Intelligence is the new flagship, portfolio-grade housing analytics product for Canada.
It keeps a clean product architecture while integrating practical Montreal analysis patterns from earlier Montreal-focused workstreams.

## What This Repository Is
- A **local-first** analytics product foundation.
- A **Streamlit application** with Montreal as the first real city implementation.
- A codebase structured for deliberate expansion to Toronto and Vancouver without infrastructure bloat.

## Migration Context
This repo upgrades and consolidates prior Montreal-only work into a cleaner architecture.

Source repos targeted for migration:
- `yumorepos/montreal-housing-dashboard`
- `yumorepos/montreal-housing-analysis`

### Brutally honest migration status
- The old repos could not be cloned from this execution environment (network proxy blocked GitHub access).
- Because of that, this migration iteration focused on integrating the **best-practice patterns** already represented in this repo and converting Montreal from demo framing into a stronger analytical city module.
- The architecture is now ready for direct code-level import from both legacy repos once network access is available.

## Current Product Capabilities (Montreal)
- Recruiter-facing Montreal dashboard with:
  - city KPI cards (rent, price, growth)
  - citywide trend charts (rent and sale price)
  - neighborhood affordability snapshot table
  - rent-vs-price scatter positioning
- Reusable analysis module (`analysis/montreal.py`) for:
  - data cleaning and validation
  - yearly city summaries
  - neighborhood affordability metrics
  - KPI calculation
- Config-driven city setup (`config/cities.yml`) keeping Toronto/Vancouver paths extensible.

## Repository Structure
```text
app/                Streamlit app
  pages/            City-facing UI modules
  utils/            Config and data access helpers
analysis/           Reusable analysis/cleaning logic
etl/                Future ingestion/transformation jobs
data/
  raw/              Raw datasets
  processed/        Curated local datasets used by dashboard
models/             Future predictive models
tests/              Unit tests for data and metric logic
config/             City and dataset configuration
docs/               Product/architecture documentation
```

## Tech Stack
- Python 3.10+
- Streamlit
- Pandas
- PyYAML
- Pytest

## Run Locally
```bash
pip install -r requirements.txt
streamlit run app/main.py
```

## Roadmap
### Next
- complete direct migration from both Montreal legacy repos once source access is available
- add Toronto dataset + city page
- add Vancouver dataset + city page

### Later
- affordability scoring model
- forecast models for rent/price trends
- geospatial neighborhood views
- scheduled ETL workflows
