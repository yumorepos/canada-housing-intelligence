# Architecture Notes

## Product direction
Canada Housing Intelligence stays intentionally lightweight and honest:
- no external services required to run
- no fake production infrastructure
- clear separation between UI composition and analytical logic
- recruiter-grade storytelling layered on top of reproducible metrics

## Module boundaries
- `app/`: Streamlit UI layout, narrative flow, and section composition only.
- `analysis/`: reusable city analytics (KPIs, growth rankings, affordability, volatility).
- `app/utils/`: thin wrappers for config loading and file-based data loading.
- `data/processed/`: app-ready local datasets.

## Montreal implementation decisions
### Kept / strengthened
- multi-city framing with Montreal as first implemented market
- config-driven dataset wiring for future city expansion
- local-first execution model

### Upgraded in this iteration
- moved additional business logic into `analysis/montreal.py`:
  - affordability ratio trend
  - neighborhood growth leader/laggard ranking
  - neighborhood volatility indicators
  - richer KPI bundle with YoY + period signals
- redesigned Montreal page hierarchy into:
  - Executive Snapshot
  - Market Trajectory
  - Neighborhood Momentum & Stability
  - Current Positioning & Affordability
  - Analyst Notes
- replaced demo-like captions with decision-support-oriented interpretation text

### Intentionally not implemented
- Toronto/Vancouver analytics modules
- external pipelines or infrastructure-heavy services
- any claims of complete line-by-line migration from blocked source repos

## Honest limitations
- Insights are based on the included local sample dataset and are directional.
- Neighborhood rankings are sensitive to sample coverage and should not be interpreted as official benchmarks.
- Direct repository-level migration from the two legacy Montreal repos is still blocked by environment GitHub access limits.
