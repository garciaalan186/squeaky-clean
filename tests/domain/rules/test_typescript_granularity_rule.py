"""Tests for TypeScriptGranularityRule."""

from pathlib import Path

from squeaky_clean.domain.rules.typescript_granularity_rule import TypeScriptGranularityRule

_CLEAN = """export class Calculator {
  add(a: number, b: number): number {
    return a + b;
  }
}
"""

_LONG = "\n".join([f"// line {i}" for i in range(90)])

_SIX_METHODS = """export class Foo {
  constructor() {}
  a(): number { return 1; }
  b(): number { return 2; }
  c(): number { return 3; }
  d(): number { return 4; }
  e(): number { return 5; }
  f(): number { return 6; }
}
"""


def _write(tmp: Path, name: str, body: str) -> Path:
    p = tmp / name
    p.write_text(body)
    return p


def test_clean_ts_file_has_no_violations(tmp_path: Path) -> None:
    path = _write(tmp_path, "calculator.ts", _CLEAN)
    assert TypeScriptGranularityRule().check(path) == []


def test_long_ts_file_violates(tmp_path: Path) -> None:
    path = _write(tmp_path, "long.ts", _LONG)
    violations = TypeScriptGranularityRule().check(path)
    assert any("lines" in v.message for v in violations)


def test_six_methods_violates(tmp_path: Path) -> None:
    path = _write(tmp_path, "six.ts", _SIX_METHODS)
    violations = TypeScriptGranularityRule().check(path)
    assert any("6 public methods" in v.message for v in violations)


def test_non_ts_file_skipped(tmp_path: Path) -> None:
    path = _write(tmp_path, "foo.js", "export class Foo {}")
    assert TypeScriptGranularityRule().check(path) == []
