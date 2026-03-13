# Architecture Notes

## Product direction
Canada Housing Intelligence is intentionally local-first and lightweight:
- no external services required to run
- no fake production infrastructure
- clear separation between UI, analysis logic, and data access

## Module boundaries
- `app/`: Streamlit UI and page composition only.
- `analysis/`: reusable metric + transformation logic.
- `app/utils/`: thin wrappers for config loading and file-based dataset loading.
- `data/processed/`: app-ready datasets.

## Migration decisions
### Kept / strengthened
- clear multi-city app framing
- modular utility-based loading
- straightforward metrics with tests
- data-driven page composition

### Rewritten lightly
- moved core metric logic into `analysis/montreal.py` to avoid KPI duplication in UI
- replaced minimal demo-only visualization with multi-section analytical view
- upgraded city config from list to city mapping for future extensibility

### Dropped (intentionally)
- placeholder-only framing that looked like a toy dashboard
- duplicated metric logic across files
- any non-integrated scripts/notebooks that do not feed product code

## Honest limitations
- Direct repository-level migration from the two legacy Montreal repos is blocked in this environment due GitHub network restrictions.
- This iteration prepares clean integration points and improves Montreal product quality, but does not claim full line-by-line import from legacy repos.
