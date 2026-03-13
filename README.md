# Canada Housing Intelligence

Canada Housing Intelligence is a recruiter-facing, local-first housing analytics product focused on making market shifts understandable in seconds.
The app now opens on a real Canada comparison page, with Montreal and Toronto available as drill-down city experiences. Vancouver remains staged as upcoming.

## What This Repository Is
- A **local-first** analytics foundation that runs without external infrastructure.
- A **Streamlit product UI** with a national comparison entry point and city intelligence pages.
- A modular codebase designed to scale city-by-city without large rewrites.

## Current Product Capabilities
### Canada overview (national comparison layer)
- **Decision snapshot metrics**
  - lower-rent city and lower-price city
  - higher-pressure city (combined rent/price growth signal)
  - strongest latest-year data coverage city
- **Cross-city comparison table**
  - latest average rent, median price, rent/price growth, affordability ratio, coverage %, listing samples
- **High-value visuals**
  - affordability now (rent vs price by city)
  - pressure comparison (rent growth vs price growth)
  - city-level affordability trend divergence over time (rent-to-price ratio)
- **Analyst notes with explicit scope caveat**
  - clear reminder that comparisons are directional and based on local/sample data

### City drill-downs (Montreal + Toronto)
Each implemented city includes:
- executive snapshot KPIs
- market trajectory charts
- neighborhood momentum with robustness guardrails
- current affordability positioning table + scatter
- concise analyst notes

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
  pages/            Canada and city-facing UI modules
  utils/            Config and data access helpers
analysis/           Reusable city and cross-city metric logic
data/
  processed/        Curated local datasets used by dashboard
tests/              Unit tests for data and metric logic
config/             City profile configuration (metadata, guardrails, status, copy)
docs/               Product/architecture documentation
```


## City Profile Configuration
City-specific metadata now lives in `config/cities.yml` and is loaded via `app/utils/config.py`.

What is centralized per city:
- display name and status (`live` vs `coming_soon`)
- subtitle and Canada-page positioning copy
- dataset path (local for now)
- guardrail thresholds (`min_years`, `min_avg_listings`, `min_avg_coverage`)

To add a new city next:
1. Add a city entry in `config/cities.yml`.
2. Mark it `enabled: true` and `status: live` once data is ready.
3. Reuse `app/pages/city_overview.py` via a thin wrapper page module.

## Run Locally
Run from the repository root:
```bash
pip install -r requirements.txt
streamlit run app/main.py
```

Import/runtime note: app entry scripts include a small `sys.path` bootstrap so Streamlit multipage execution can resolve both `app.*` and `analysis.*` imports reliably from root.

## Brutally Honest Limitations
- Data is still local/sample and synthetic; this is not an official benchmark feed.
- National comparison only includes currently implemented cities (Montreal and Toronto).
- Cross-city comparisons are directional because sample support can differ by city and neighborhood.
- Vancouver is not implemented yet.

## Recommended Next Highest-Leverage Step
Add a shared city profile configuration layer (per-city thresholds, metadata, and narrative copy) so enabling Vancouver becomes mostly a data + config operation with minimal UI changes.
