from __future__ import annotations

import argparse
import dis
import sys
from pathlib import Path
from types import CodeType

import pytest
import trace

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run pytest and enforce a minimum executable-line coverage threshold.")
    parser.add_argument("--min-coverage", type=float, default=0.50, help="Minimum required coverage ratio (0-1).")
    parser.add_argument("--targets", nargs="+", default=["app", "analysis", "scripts"], help="Directories to include.")
    parser.add_argument("pytest_args", nargs=argparse.REMAINDER, help="Args passed through to pytest (prefix with --).")
    return parser.parse_args()


def _iter_python_files(target_dirs: list[str]) -> list[Path]:
    files: list[Path] = []
    for target in target_dirs:
        root = (ROOT / target).resolve()
        if not root.exists() or not root.is_dir():
            continue
        for path in root.rglob("*.py"):
            if path.name == "__init__.py":
                continue
            files.append(path)
    return sorted(files)


def _collect_code_lines(code: CodeType) -> set[int]:
    lines = {line for _, line in dis.findlinestarts(code) if line > 0}
    for const in code.co_consts:
        if isinstance(const, CodeType):
            lines.update(_collect_code_lines(const))
    return lines


def _file_executable_lines(path: Path) -> set[int]:
    code = compile(path.read_text(encoding="utf-8"), str(path), "exec")
    return _collect_code_lines(code)


def _normalize_counts(raw_counts: dict[tuple[str, int], int]) -> dict[str, set[int]]:
    normalized: dict[str, set[int]] = {}
    for (filename, line), count in raw_counts.items():
        if count <= 0:
            continue
        resolved = str(Path(filename).resolve())
        normalized.setdefault(resolved, set()).add(line)
    return normalized


def main() -> None:
    args = _parse_args()
    files = _iter_python_files(args.targets)
    if not files:
        raise SystemExit("No target files found.")

    pytest_args = args.pytest_args[1:] if args.pytest_args and args.pytest_args[0] == "--" else args.pytest_args
    if not pytest_args:
        pytest_args = ["-q"]

    tracer = trace.Trace(count=1, trace=0)
    exit_code = tracer.runfunc(pytest.main, pytest_args)
    results = tracer.results()
    executed = _normalize_counts(results.counts)

    total_executable = 0
    total_hit = 0
    breakdown: list[tuple[str, int, int, float]] = []

    for file_path in files:
        executable_lines = _file_executable_lines(file_path)
        if not executable_lines:
            continue
        hit = len(executable_lines.intersection(executed.get(str(file_path.resolve()), set())))
        total_executable += len(executable_lines)
        total_hit += hit
        ratio = hit / len(executable_lines)
        breakdown.append((str(file_path.relative_to(ROOT)), hit, len(executable_lines), ratio))

    overall = (total_hit / total_executable) if total_executable else 0.0
    print(f"Coverage summary: {total_hit}/{total_executable} executable lines = {overall:.2%}")
    print("Lowest-coverage files:")
    for file_name, hit, total, ratio in sorted(breakdown, key=lambda row: row[3])[:8]:
        print(f"  - {file_name}: {hit}/{total} ({ratio:.2%})")

    if exit_code != 0:
        raise SystemExit(exit_code)
    if overall < args.min_coverage:
        raise SystemExit(
            f"Coverage gate failed: {overall:.2%} is below required minimum {args.min_coverage:.2%}."
        )


if __name__ == "__main__":
    main()
