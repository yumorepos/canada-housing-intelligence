# Architecture Notes

## Product direction
Canada Housing Intelligence stays intentionally lightweight and honest:
- no external services required to run
- no fake production infrastructure
- clear separation between UI composition and analytical logic
- recruiter-grade storytelling layered on top of reproducible metrics

## Module boundaries
- `app/`: Streamlit UI layout, narrative flow, and section composition only.
- `analysis/`: reusable city analytics (KPIs, growth rankings, affordability, volatility, confidence guardrails).
- `app/utils/`: thin wrappers for config loading and file-based data loading.
- `data/processed/`: app-ready local datasets.

## Montreal data-layer decisions
### Data shape improvements
- Expanded local Montreal sample to include more neighborhoods and longer time coverage.
- Added contextual fields used directly by analytics:
  - `borough`
  - `listing_count`
  - `sales_count`
  - `coverage_score`
  - `property_type`

### Robustness guardrails
Implemented in `analysis/montreal.py` and kept out of UI:
- ranking eligibility thresholds:
  - minimum years observed
  - minimum average listing count
  - minimum average coverage score
- explicit support classification:
  - `robust`
  - `directional`
- coverage summaries for UI-level caveats without warning overload

### UI integration principles
- Surface confidence/coverage in a compact way (single coverage snapshot + ranking guardrail caption).
- Use robust sample only for leader/laggard callouts and volatility interpretation.
- Keep directional neighborhoods visible in tables for transparency.

## Intentionally not implemented
- Toronto/Vancouver analytics modules
- external pipelines or infrastructure-heavy services
- claims of official benchmark quality

## Honest limitations
- Dataset remains local/sample and is still synthetic rather than sourced from authoritative feeds.
- Guardrails improve trustworthiness but do not make the outputs statistically official.
- Direct repository-level migration from the two legacy Montreal repos is still blocked by environment GitHub access limits.
