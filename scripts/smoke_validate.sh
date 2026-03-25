#!/usr/bin/env bash
set -euo pipefail

python -m pip install --upgrade pip
pip install -r requirements.txt
pytest -q
python scripts/coverage_gate.py --min-coverage 0.50 --targets app analysis scripts -- -q
python scripts/data_health_check.py \
  --config config/cities.yml \
  --contract config/data_contract.yml \
  --sources config/sources.yml \
  --report-out artifacts/data_health_report.json

echo "Smoke validation passed."
