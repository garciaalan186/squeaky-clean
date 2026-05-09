"""Tests for PythonGranularityRule."""

from pathlib import Path

from squeaky_clean.domain.rules.python_granularity_rule import PythonGranularityRule

_CLEAN = """class Foo:
    def bar(self) -> int:
        return 1
"""

_LONG = "\n".join([f"# line {i}" for i in range(90)])

_FOUR_METHODS = """class Foo:
    def a(self) -> int: return 1
    def b(self) -> int: return 1
    def c(self) -> int: return 1
    def d(self) -> int: return 1
"""

_THREE_ARGS = """class Foo:
    def bar(self, a: int, b: int, c: int) -> int:
        return a + b + c
"""

_TWO_CLASSES = """class Foo:
    pass

class Bar:
    pass
"""


def _write(tmp: Path, name: str, body: str) -> Path:
    p = tmp / name
    p.write_text(body)
    return p


def test_clean_file_has_no_violations(tmp_path: Path) -> None:
    path = _write(tmp_path, "clean.py", _CLEAN)
    assert PythonGranularityRule().check(path) == []


def test_long_file_violates(tmp_path: Path) -> None:
    path = _write(tmp_path, "long.py", _LONG)
    violations = PythonGranularityRule().check(path)
    assert any("lines" in v.message for v in violations)


def test_four_methods_violates(tmp_path: Path) -> None:
    path = _write(tmp_path, "four.py", _FOUR_METHODS)
    violations = PythonGranularityRule().check(path)
    assert any("public methods" in v.message for v in violations)


def test_three_args_violates(tmp_path: Path) -> None:
    path = _write(tmp_path, "args.py", _THREE_ARGS)
    violations = PythonGranularityRule().check(path)
    assert any("args" in v.message for v in violations)


def test_two_classes_violates(tmp_path: Path) -> None:
    path = _write(tmp_path, "two.py", _TWO_CLASSES)
    violations = PythonGranularityRule().check(path)
    assert any("classes" in v.message for v in violations)
