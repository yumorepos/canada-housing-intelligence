# Architecture Notes

## Product direction
Canada Housing Intelligence stays intentionally lightweight and honest:
- no external services required to run
- no cloud pipeline or orchestration
- clear separation between UI composition and analytical logic
- explicit provenance and mode signaling to improve trust

## National + city architecture
- `analysis/city_metrics.py` hosts reusable city analytics and Canada comparison helpers.
- `app/pages/canada_overview.py` is the national entry point for cross-city tradeoff analysis.
- `app/pages/city_overview.py` provides a reusable city layout used by Montreal, Toronto, and Vancouver.
- City-specific files remain thin wrappers.
- `app/main.py` routes to Canada overview first, then resolves city page renderers dynamically using the `app.pages.<city>_overview` naming convention.

## Data architecture: raw -> processed -> app
### Raw layer (manual local drop)
- Directory: `data/raw/`
- Team can place externally sourced CSV extracts here.

### Processing layer
- `app/utils/ingestion.py` handles transformation and provenance enrichment.
- `scripts/process_housing_raw.py` is a lightweight CLI wrapper for raw-to-processed generation.
- `config/data_contract.yml` defines required/optional raw columns and type/range expectations.
- processing writes a run manifest with input/output SHA256 + run metadata under `data/processed/manifests/` (or explicit path).
- Output defaults to `data/processed/housing_source_processed.csv`.

### App read layer
- `app/utils/data_loader.py` loads the primary processed dataset and falls back to `data/processed/housing_sample.csv` when needed.
- Loader returns both cleaned data and compact provenance metadata for UI display.

## Data model
### Core analysis fields
- `city`, `neighborhood`, `year`, `average_rent`, `median_price`
- `borough`, `listing_count`, `sales_count`, `coverage_score`, `property_type`

### Provenance fields
- `source_name`, `source_type`, `source_period`, `processed_at`
- `coverage_note`, `confidence_note`, `data_mode`

Analysis functions remain compatible because they require only core fields and ignore extra metadata columns.

## Guardrails and trust
Implemented in shared analysis logic and kept out of UI business logic:
- minimum years observed
- minimum average listing count
- minimum average coverage score
- robust vs directional support tiering

UI now adds provenance context (mode/source/period), coverage/confidence notes, and freshness status based on `processed_at`.

## Honest limitations
- ingestion is manual local-first, not automated
- provenance is row-level static metadata today
- source-backed credibility depends on external file quality and user discipline
- no built-in schema versioning yet

## Claim-to-Implementation Truth Mapping

### Claim: "CI enforces repository health checks"
- **Implemented by:** `.github/workflows/ci.yml`
- **What is actually enforced:** dependency install from `requirements.txt`, bytecode compilation, lint (`ruff`), types (`mypy`), and `pytest`.
- **Non-guarantees:** CI does not validate external source APIs or cloud deployment.

### Claim: "Data freshness can be checked automatically"
- **Implemented by:** `.github/workflows/data-health.yml`, `scripts/data_health_check.py`
- **What is actually enforced:** scheduled/manual workflow runs freshness + contract checks and uploads JSON report artifact.
- **Non-guarantees:** it does not auto-ingest new raw data files.

### Claim: "Local-first source-backed workflow exists"
- **Implemented by:** `scripts/process_housing_raw.py`, `app/utils/ingestion.py`, `app/utils/data_loader.py`
- **What is actually enforced:** required ingestion columns, processed output writing, fallback to sample if primary processed file is missing.
- **Non-guarantees:** no automated orchestration/scheduling; no freshness SLA monitor.

### Claim: "Trust/provenance context is surfaced"
- **Implemented by:** provenance columns in processed data and UI captions in app pages.
- **What is actually enforced:** source name/type/period + mode labels are shown in UI.
- **Non-guarantees:** no external provenance registry (lineage remains repo-local manifests).
