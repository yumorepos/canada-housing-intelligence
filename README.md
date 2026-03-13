# Canada Housing Intelligence

Canada Housing Intelligence is a recruiter-facing, local-first housing analytics product focused on making market shifts understandable in seconds.
Montreal and Toronto are now fully implemented city experiences, with Vancouver staged as the next expansion.

## What This Repository Is
- A **local-first** analytics foundation that runs without external infrastructure.
- A **Streamlit product UI** with polished city intelligence pages.
- A modular codebase designed to scale city-by-city without large rewrites.

## Current Product Capabilities (Montreal + Toronto)
Each implemented city now includes:
- **Executive snapshot KPIs**
  - latest average rent and sale price
  - YoY rent/price change
  - period growth and rent-to-price ratio shift
  - latest sample coverage and listing-observation totals
- **Market trajectory section**
  - citywide rent/price trend
  - affordability ratio trend (annual rent / median price)
- **Neighborhood momentum section**
  - robust-only rent growth leaders/laggards
  - robust-only price growth leaders/laggards
  - neighborhood stability signal via growth volatility
- **Current positioning section**
  - latest affordability snapshot table with coverage fields
  - rent-vs-price positioning scatter
- **Analyst notes**
  - concise interpretation of affordability pressure, momentum dispersion, and stability

## Local Dataset (sample, not official)
`data/processed/housing_sample.csv` contains local sample records for Montreal and Toronto.

Fields used by analysis:
- `city`, `neighborhood`, `year`, `average_rent`, `median_price`
- `borough` (grouping for interpretation and visuals)
- `listing_count` (sample support proxy)
- `sales_count` (supplemental context)
- `coverage_score` (0-1 local confidence proxy)
- `property_type` (currently `all`, reserved for later segmentation)

Guardrails for neighborhood rankings:
- minimum years observed
- minimum average listing support
- minimum average coverage score

Neighborhoods failing thresholds are retained as directional context, but excluded from robust leader/laggard callouts.

All insights are derived from a local sample dataset and should be treated as directional, not official citywide estimates.

## Repository Structure
```text
app/                Streamlit app
  pages/            City-facing UI modules
  utils/            Config and data access helpers
analysis/           Reusable city metric and transformation logic
data/
  processed/        Curated local datasets used by dashboard
tests/              Unit tests for data and metric logic
config/             City and dataset configuration
docs/               Product/architecture documentation
```

## Run Locally
```bash
pip install -r requirements.txt
streamlit run app/main.py
```

## Brutally Honest Limitations
- Data is still local/sample and synthetic; this is not an official benchmark feed.
- Cross-city comparisons should be interpreted as directional because sample support differs by neighborhood.
- Vancouver is not implemented yet.

## Recommended Next Highest-Leverage Step
Add a shared city profile layer (per-city metadata, thresholds, and narrative copy in config) so Vancouver can be enabled by adding data + one small page wrapper.
