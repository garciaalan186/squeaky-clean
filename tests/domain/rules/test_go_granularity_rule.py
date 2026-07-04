"""Tests for GoGranularityRule."""

from pathlib import Path

from squeaky_clean.domain.rules.go_granularity_rule import GoGranularityRule

_CLEAN = """\
package foo

func Add(a int, b int) int {
    return a + b
}
"""

_LONG = "\n".join([f"// line {i}" for i in range(90)])

_SIX_METHODS = """\
package foo

type Calc struct{}

func (c *Calc) A() int { return 1 }
func (c *Calc) B() int { return 2 }
func (c *Calc) C() int { return 3 }
func (c *Calc) D() int { return 4 }
func (c *Calc) E() int { return 5 }
func (c *Calc) F() int { return 6 }
"""


def _write(tmp: Path, name: str, body: str) -> Path:
    p = tmp / name
    p.write_text(body)
    return p


def test_clean_go_file_has_no_violations(tmp_path: Path) -> None:
    path = _write(tmp_path, "calc.go", _CLEAN)
    assert GoGranularityRule().check(path) == []


def test_long_go_file_violates(tmp_path: Path) -> None:
    path = _write(tmp_path, "long.go", _LONG)
    violations = GoGranularityRule().check(path)
    assert any("lines" in v.message for v in violations)


def test_six_exported_methods_on_struct_violates(tmp_path: Path) -> None:
    path = _write(tmp_path, "calc.go", _SIX_METHODS)
    violations = GoGranularityRule().check(path)
    assert any("6 exported funcs" in v.message for v in violations)


def test_non_go_file_skipped(tmp_path: Path) -> None:
    path = _write(tmp_path, "foo.py", "class Foo: pass\n")
    assert GoGranularityRule().check(path) == []


def test_test_go_file_skipped(tmp_path: Path) -> None:
    path = _write(tmp_path, "foo_test.go", _LONG)
    assert GoGranularityRule().check(path) == []
