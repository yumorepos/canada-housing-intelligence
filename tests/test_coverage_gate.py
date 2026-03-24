from pathlib import Path

from scripts.coverage_gate import _collect_code_lines, _normalize_counts


def test_collect_code_lines_captures_nested_blocks(tmp_path: Path):
    code = compile(
        """
def outer():
    x = 1
    def inner():
        return x + 1
    return inner()
""",
        str(tmp_path / "nested.py"),
        "exec",
    )

    lines = _collect_code_lines(code)

    assert {2, 3, 4, 5}.issubset(lines)


def test_normalize_counts_ignores_non_positive_hits(tmp_path: Path):
    a = str((tmp_path / "a.py").resolve())
    b = str((tmp_path / "b.py").resolve())
    normalized = _normalize_counts({(a, 10): 1, (a, 11): 0, (b, 2): -1})
    assert normalized == {a: {10}}
