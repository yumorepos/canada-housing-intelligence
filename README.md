# Canada Housing Intelligence

Canada Housing Intelligence is a recruiter-facing, local-first housing analytics product focused on making market shifts understandable in seconds.
Montreal is the first fully implemented city and now serves as a decision-support experience rather than a simple dashboard demo.

## What This Repository Is
- A **local-first** analytics foundation that runs without external infrastructure.
- A **Streamlit product UI** with a polished Montreal intelligence page.
- A modular codebase designed to scale to Toronto and Vancouver without rework.

## Migration Context
This repo consolidates and upgrades prior Montreal-focused work patterns into a cleaner architecture.

Source repos originally targeted for migration:
- `yumorepos/montreal-housing-dashboard`
- `yumorepos/montreal-housing-analysis`

### Brutally honest migration status
- The old repos could not be cloned from this execution environment due network/proxy restrictions.
- This iteration **does not claim a full source-level migration** from those repositories.
- Instead, it upgrades this repo's Montreal implementation into a stronger product experience with cleaner analysis boundaries.

## Current Product Capabilities (Montreal)
The Montreal page now includes:
- **Executive snapshot KPIs**
  - latest average rent and sale price
  - YoY rent/price change
  - period growth and rent-to-price ratio shift
- **Market trajectory section**
  - citywide rent/price trend
  - affordability ratio trend (annual rent / median price)
- **Neighborhood momentum section**
  - rent growth leaders/laggards
  - price growth leaders/laggards
  - neighborhood stability signal via growth volatility
- **Current positioning section**
  - latest affordability snapshot table
  - rent-vs-price positioning scatter
- **Analyst notes**
  - concise interpretation of affordability pressure, momentum dispersion, and stability

All insights are derived from the local sample dataset in `data/processed/housing_sample.csv` and should be treated as directional, not official citywide estimates.

## Repository Structure
```text
app/                Streamlit app
  pages/            City-facing UI modules
  utils/            Config and data access helpers
analysis/           Reusable metric and transformation logic
data/
  processed/        Curated local datasets used by dashboard
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
### Next highest leverage
- integrate a richer Montreal dataset (additional neighborhoods + transaction volume/context columns) to improve reliability of ranking and volatility insights

### Later
- complete direct source-level migration from the two legacy Montreal repos once network access is available
- add Toronto dataset + city page
- add Vancouver dataset + city page
- add affordability scoring model
- add forecast models for rent/price trends
- add geospatial neighborhood views
