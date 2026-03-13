# Architecture Notes

## Product direction
Canada Housing Intelligence stays intentionally lightweight and honest:
- no external services required to run
- no fake production infrastructure
- clear separation between UI composition and analytical logic
- recruiter-grade storytelling layered on top of reproducible metrics

## Multi-city architecture
- `analysis/city_metrics.py` now hosts reusable city analytics for all implemented cities.
- `analysis/montreal.py` remains as a compatibility shim, forwarding to shared analysis helpers.
- `app/pages/city_overview.py` provides a reusable recruiter-facing city page layout.
- City-specific page files (`montreal_overview.py`, `toronto_overview.py`) only provide city identity + narrative subtitle.

## Module boundaries
- `app/`: Streamlit UI layout and page routing.
- `analysis/`: reusable analytics (KPIs, growth rankings, affordability, volatility, confidence guardrails).
- `app/utils/`: thin wrappers for config loading and file-based data loading.
- `data/processed/`: app-ready local datasets.

## Data-layer decisions
### Data shape
- Shared schema used for both Montreal and Toronto:
  - `city`, `neighborhood`, `year`, `average_rent`, `median_price`
  - `borough`, `listing_count`, `sales_count`, `coverage_score`, `property_type`

### Guardrails
Implemented in shared analysis logic and kept out of UI:
- ranking eligibility thresholds:
  - minimum years observed
  - minimum average listing count
  - minimum average coverage score
- explicit support classification:
  - `robust`
  - `directional`
- coverage summaries for UI-level caveats without warning overload

## Honest limitations
- Dataset remains local/sample and synthetic rather than sourced from authoritative feeds.
- Guardrails improve trustworthiness but do not make outputs statistically official.
- Vancouver remains roadmap only.
