from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.utils.ingestion import validate_raw_data_contract


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run data freshness + schema health checks.")
    parser.add_argument("--config", default="config/cities.yml", help="Path to cities config.")
    parser.add_argument("--contract", default="config/data_contract.yml", help="Path to data contract YAML.")
    parser.add_argument("--sources", default="config/sources.yml", help="Path to source manifest YAML.")
    parser.add_argument("--dataset", default=None, help="Override dataset path (defaults to shared_defaults.dataset_path).")
    parser.add_argument("--report-out", default="artifacts/data_health_report.json", help="Output report JSON path.")
    return parser.parse_args()


def _load_yaml(path: str) -> dict:
    with Path(path).open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def main() -> None:
    args = _parse_args()
    config = _load_yaml(args.config)
    contract = _load_yaml(args.contract)
    sources_manifest = _load_yaml(args.sources)

    defaults = config.get("shared_defaults", {})
    dataset_path = args.dataset or defaults.get("dataset_path")
    max_age_days = int(defaults.get("freshness", {}).get("max_age_days", 45))
    result: dict[str, object] = {
        "checked_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "dataset_path": dataset_path,
        "max_age_days": max_age_days,
        "status": "pass",
        "errors": [],
    }

    if not dataset_path or not Path(dataset_path).exists():
        result["status"] = "fail"
        result["errors"] = ["dataset_missing"]
    else:
        data = pd.read_csv(dataset_path)
        try:
            validate_raw_data_contract(data, contract)
        except ValueError as exc:
            result["status"] = "fail"
            result["errors"] = [f"contract_validation_failed:{exc}"]
        else:
            known_sources = {
                str(source.get("name", "")).strip(): source
                for source in sources_manifest.get("sources", [])
                if str(source.get("name", "")).strip()
            }
            source_name = None
            if "source_name" in data.columns:
                values = [v for v in data["source_name"].dropna().astype(str).tolist() if v.strip()]
                if values:
                    source_name = values[0]

            if source_name and source_name not in known_sources:
                result["status"] = "fail"
                result["errors"] = [f"unknown_source:{source_name}"]
                report_path = Path(args.report_out)
                report_path.parent.mkdir(parents=True, exist_ok=True)
                report_path.write_text(json.dumps(result, indent=2), encoding="utf-8")
                print(json.dumps(result, indent=2))
                raise SystemExit(1)

            processed_at = None
            if "processed_at" in data.columns:
                values = [v for v in data["processed_at"].dropna().astype(str).tolist() if v.strip()]
                if values:
                    processed_at = values[0]
            if processed_at:
                parsed = datetime.fromisoformat(processed_at.replace("Z", "+00:00"))
                if parsed.tzinfo is None:
                    parsed = parsed.replace(tzinfo=UTC)
                age_days = (datetime.now(UTC) - parsed).days
                result["data_age_days"] = age_days
                source_cadence_days = None
                if source_name and source_name in known_sources:
                    source_cadence_days = int(known_sources[source_name].get("cadence_max_age_days", max_age_days))
                    result["source_name"] = source_name
                    result["source_cadence_max_age_days"] = source_cadence_days
                threshold_days = source_cadence_days if source_cadence_days is not None else max_age_days
                if age_days > threshold_days:
                    result["status"] = "fail"
                    result["errors"] = [f"stale_data:{age_days}d>{threshold_days}d"]
            else:
                result["status"] = "fail"
                result["errors"] = ["processed_at_missing"]

    report_path = Path(args.report_out)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(json.dumps(result, indent=2))
    if result["status"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
