from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.utils.ingestion import process_raw_housing_file


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Transform local raw housing CSV into processed app dataset.")
    parser.add_argument("--raw", required=True, help="Path to raw CSV (for example data/raw/housing_source.csv)")
    parser.add_argument("--out", required=True, help="Path for processed CSV output")
    parser.add_argument("--source-name", required=True, help="Human-readable source name")
    parser.add_argument("--source-type", default="csv_extract", help="Source type label")
    parser.add_argument(
        "--data-contract",
        default="config/data_contract.yml",
        help="Path to YAML data contract used to validate required raw columns/types",
    )
    parser.add_argument("--source-period", default=None, help="Coverage period label, e.g. 2018-2024")
    parser.add_argument(
        "--manifest-out",
        default=None,
        help="Optional explicit path for lineage manifest JSON (default writes under data/processed/manifests/)",
    )
    parser.add_argument(
        "--coverage-note",
        default="Coverage varies by city and neighborhood.",
        help="Coverage disclaimer stored in processed rows",
    )
    parser.add_argument(
        "--confidence-note",
        default="Directional confidence only; not an official benchmark feed.",
        help="Confidence disclaimer stored in processed rows",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()
    processed = process_raw_housing_file(
        raw_path=args.raw,
        output_path=args.out,
        source_name=args.source_name,
        source_type=args.source_type,
        data_contract_path=args.data_contract,
        manifest_path=args.manifest_out,
        source_period=args.source_period,
        coverage_note=args.coverage_note,
        confidence_note=args.confidence_note,
    )
    print(f"Wrote {len(processed)} rows to {args.out}")


if __name__ == "__main__":
    main()
