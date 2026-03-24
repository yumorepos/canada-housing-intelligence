# Canada Housing Intelligence

[![CI](https://github.com/yumorepos/canada-housing-intelligence/actions/workflows/ci.yml/badge.svg)](https://github.com/yumorepos/canada-housing-intelligence/actions/workflows/ci.yml)


Canada Housing Intelligence is a recruiter-facing, local-first housing analytics product focused on making market shifts understandable in seconds.
The app opens on a Canada comparison page, with Montreal, Toronto, and Vancouver as live city drill-downs.

## What This Repository Is
- A **local-first** analytics foundation that runs without external infrastructure.
- A **Streamlit product UI** with a national comparison entry point and city intelligence pages.
- A practical **source-backed ingestion path** that still supports sample-data fallback.

## Current Product Capabilities

### Interactive Map
An interactive map showing Canadian cities with housing data, color-coded by affordability.  Click [here](map.html) to view the map.

## Current Product Capabilities
### Canada overview (national comparison layer)
- Decision snapshot metrics (lower-rent city, lower-price city, pressure, coverage)
- Cross-city comparison table (rent, price, growth, affordability ratio, coverage, listing samples)
- Cross-city visuals and analyst notes

### City drill-downs (Montreal + Toronto + Vancouver)
Each implemented city includes:
- executive KPI snapshot
- market trajectory charts
- neighborhood momentum with robustness guardrails
- affordability snapshot table + scatter
- concise analyst notes

## Data Workflow (Local-first, source-backed)
### Processed datasets used by the app
- Primary processed path: `data/processed/housing_source_processed.csv`
- Fallback processed path: `data/processed/housing_sample.csv`

If the primary source-backed processed file is missing, the app automatically falls back to sample data so local usability remains intact.

### Ingestion flow
1. Drop a raw CSV into `data/raw/` (manual local workflow).
2. Run:
   ```bash
   python scripts/process_housing_raw.py \
     --raw data/raw/<your_file>.csv \
     --out data/processed/housing_source_processed.csv \
     --source-name "<source name>" \
     --source-type "manual_csv_drop" \
     --source-period "2018-2024"
   ```
3. Launch app:
   ```bash
   streamlit run app/main.py
   ```

Transformation logic is in `app/utils/ingestion.py` and validates raw inputs against `config/data_contract.yml` before writing app-compatible output.
Each ingestion run also writes a lineage manifest with input/output hashes and run metadata (default under `data/processed/manifests/`).

## Provenance fields
Processed rows can include:
- `source_name`
- `source_type`
- `source_period`
- `processed_at`
- `coverage_note`
- `confidence_note`
- `data_mode` (`source_backed` for processed source outputs)

The UI surfaces compact provenance context (data mode + source + period) without warning spam.

## Repository Structure
```text
app/                Streamlit app
  pages/            Canada and city-facing UI modules
  utils/            Config, ingestion, and data access helpers
analysis/           Reusable city and cross-city metric logic
data/
  raw/              Manually dropped source files (local workflow)
  processed/        App-ready processed datasets
docs/               Product/architecture documentation
scripts/            Local utility scripts (raw->processed)
tests/              Unit tests for config, ingestion, and metrics
config/             City profile configuration
```

## Run Locally
Run from the repository root:
```bash
pip install -r requirements.txt
streamlit run app/main.py
```

## Demo Walkthrough
- Use `docs/demo_playbook.md` for a repeatable recruiter-facing flow with trust-first callouts.
- Screenshot/GIF capture for trust-aware UI states is currently tracked as a manual follow-up task (blocked in this non-browser execution environment).

## Brutally Honest Limitations
- This is still a local workflow with manual file drops, not a production data pipeline.
- Source-backed mode is only as credible as the raw files you provide.
- Freshness is shown in-app from `processed_at`, but no automated scheduler updates source files.
- There is no external schema registry (the contract is local to this repo).
- Cross-city comparisons remain directional and should not be presented as official benchmark quality.

## Truth Map: Current Guarantees vs Non-Guarantees
### What is guaranteed today
- CI now fails the build if dependency install, bytecode compilation, or tests fail.
- Core local workflow is stable: raw CSV -> `scripts/process_housing_raw.py` -> processed CSV -> Streamlit app.
- Fallback behavior is explicit: if source-backed processed data is missing, app reads sample data.
- Core required analysis schema is enforced during ingestion and cleaning (`city`, `neighborhood`, `year`, `average_rent`, `median_price`).

### What is explicitly not guaranteed today
- No automated source ingestion/orchestration from external providers.
- No formal external schema registry service (contract is repo-local YAML).
- No external provenance registry (lineage manifests are local repository artifacts).
- No claim of benchmark-grade or causal statistical certainty; insights remain directional.

## Recommended Next Highest-Leverage Step
Add a lightweight `config/sources.yml` manifest (source descriptions + update cadence) and enforce source-level cadence checks in CI for stronger trust without heavy infrastructure.

## Quality Gates (CI)
Current CI enforces:
- bytecode compile checks (`python -m compileall app analysis scripts tests`)
- lint (`ruff check app analysis scripts tests`)
- type checks (`mypy app analysis scripts`)
- tests (`pytest -q`)

Coverage threshold gating is planned but not yet enforced in this repository.

## Data Health Workflow
- `.github/workflows/data-health.yml` runs on a weekly schedule and manual dispatch.
- It executes `scripts/data_health_check.py`, validates freshness + required columns, and uploads `artifacts/data_health_report.json`.

## Dependency Locking
- `requirements.txt` is pinned to exact versions used by CI.
- `requirements-lock.txt` mirrors the pinned runtime/tooling set for deterministic setup.
