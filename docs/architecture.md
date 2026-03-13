# Architecture Notes

## Product direction
Canada Housing Intelligence stays intentionally lightweight and honest:
- no external services required to run
- no fake production infrastructure
- clear separation between UI composition and analytical logic
- recruiter-grade storytelling layered on top of reproducible metrics

## National + city architecture
- `analysis/city_metrics.py` hosts reusable city analytics and Canada comparison helpers.
- `app/pages/canada_overview.py` is the national product entry point for cross-city tradeoff analysis.
- `app/pages/city_overview.py` provides a reusable city layout used by Montreal and Toronto.
- City-specific files (`montreal_overview.py`, `toronto_overview.py`) remain thin identity wrappers.
- `app/main.py` routes first to Canada overview, then city drill-down pages.

## Module boundaries
- `app/`: Streamlit UI layout and page routing.
- `analysis/`: reusable analytics (KPIs, growth rankings, affordability, volatility, guardrails, Canada comparisons).
- `app/utils/`: thin wrappers for config loading and file-based data loading.
- `data/processed/`: app-ready local datasets.

## Data-layer decisions
### Data shape
- Shared schema used for both Montreal and Toronto:
  - `city`, `neighborhood`, `year`, `average_rent`, `median_price`
  - `borough`, `listing_count`, `sales_count`, `coverage_score`, `property_type`

### Guardrails
Implemented in shared analysis logic and kept out of UI:
- neighborhood ranking eligibility thresholds:
  - minimum years observed
  - minimum average listing count
  - minimum average coverage score
- explicit support classification:
  - `robust`
  - `directional`
- coverage summaries for UI-level caveats without warning overload

### Canada comparison layer
Implemented as analysis helpers so UI stays presentation-only:
- `canada_city_comparison`: builds normalized city comparison rows from existing KPI logic
- `canada_comparison_insights`: emits concise tradeoff signals used in executive notes
- `canada_multi_city_trends`: builds annual city-level trend series for comparison charts

## Honest limitations
- Dataset remains local/sample and synthetic rather than sourced from authoritative feeds.
- Guardrails improve trustworthiness but do not make outputs statistically official.
- National comparison currently includes only implemented cities.
- Vancouver remains roadmap only.
