"""Tests for RustGranularityRule."""

from pathlib import Path

from squeaky_clean.domain.rules.rust_granularity_rule import RustGranularityRule

_CLEAN = """\
pub struct Calc;

impl Calc {
    pub fn add(&self, a: i32, b: i32) -> i32 {
        a + b
    }
}
"""

_LONG = "\n".join([f"// line {i}" for i in range(90)])

_FOUR_FNS = """\
pub struct Calc;

impl Calc {
    pub fn a(&self) -> i32 { 1 }
    pub fn b(&self) -> i32 { 2 }
    pub fn c(&self) -> i32 { 3 }
    pub fn d(&self) -> i32 { 4 }
}
"""

_THREE_ARGS = """\
pub fn bar(a: i32, b: i32, c: i32) -> i32 { a + b + c }
"""


def _write(tmp: Path, name: str, body: str) -> Path:
    p = tmp / name
    p.write_text(body)
    return p


def test_clean_rust_file_has_no_violations(tmp_path: Path) -> None:
    path = _write(tmp_path, "calc.rs", _CLEAN)
    assert RustGranularityRule().check(path) == []


def test_long_rust_file_violates(tmp_path: Path) -> None:
    path = _write(tmp_path, "long.rs", _LONG)
    violations = RustGranularityRule().check(path)
    assert any("lines" in v.message for v in violations)


def test_four_pub_fns_violates(tmp_path: Path) -> None:
    path = _write(tmp_path, "calc.rs", _FOUR_FNS)
    violations = RustGranularityRule().check(path)
    assert any("pub fns" in v.message for v in violations)


def test_three_args_method_violates(tmp_path: Path) -> None:
    path = _write(tmp_path, "calc.rs", _THREE_ARGS)
    violations = RustGranularityRule().check(path)
    assert any("3 args" in v.message for v in violations)


def test_non_rust_file_skipped(tmp_path: Path) -> None:
    path = _write(tmp_path, "foo.py", "class Foo: pass\n")
    assert RustGranularityRule().check(path) == []
