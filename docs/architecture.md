# Architecture Notes

## Design Principles
- **Local-first**: data and dashboard run without external services.
- **Minimal dependencies**: only Streamlit, Pandas, and YAML parsing.
- **Scalable by city**: shared utilities + city-specific dashboard modules.

## Current Flow
1. `config/cities.yml` defines supported cities and default dataset.
2. `app/main.py` loads config and dataset.
3. Page modules (starting with Montreal) compute metrics and render visualizations.
4. Future ETL and models can write outputs into `data/processed/` for direct dashboard consumption.

## Expansion Path
- Add ETL jobs in `etl/` to ingest public rental and property datasets.
- Store cleaned city-level files in `data/processed/`.
- Add affordability and livability scoring in `analysis/` and `models/`.
- Extend dashboard pages in `app/pages/` for Toronto and Vancouver.
