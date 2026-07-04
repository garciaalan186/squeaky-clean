"""Tests for JavaGranularityRule."""

from pathlib import Path

from squeaky_clean.domain.rules.java_granularity_rule import JavaGranularityRule

_CLEAN = """\
// Calculator service.
public class Calculator {
    public int add(int a, int b) {
        return a + b;
    }
}
"""

_LONG = "\n".join([f"// line {i}" for i in range(90)])

_TWO_CLASSES = """\
public class Foo {}

class Bar {}
"""

_SIX_METHODS = """\
public class Foo {
    public Foo() {}
    public int a() { return 1; }
    public int b() { return 2; }
    public int c() { return 3; }
    public int d() { return 4; }
    public int e() { return 5; }
    public int f() { return 6; }
}
"""

_THREE_ARGS = """\
public class Foo {
    public int bar(int a, int b, int c) { return a + b + c; }
}
"""

_CONSTRUCTOR_NOT_COUNTED = """\
public class Foo {
    public Foo(int a, int b) {}
    public int m1() { return 1; }
    public int m2() { return 2; }
    public int m3() { return 3; }
}
"""


def _write(tmp: Path, name: str, body: str) -> Path:
    p = tmp / name
    p.write_text(body)
    return p


def test_clean_java_file_has_no_violations(tmp_path: Path) -> None:
    path = _write(tmp_path, "Calculator.java", _CLEAN)
    assert JavaGranularityRule().check(path) == []


def test_long_java_file_violates(tmp_path: Path) -> None:
    path = _write(tmp_path, "Long.java", _LONG)
    violations = JavaGranularityRule().check(path)
    assert any("lines" in v.message for v in violations)


def test_two_classes_java_file_violates(tmp_path: Path) -> None:
    path = _write(tmp_path, "Two.java", _TWO_CLASSES)
    violations = JavaGranularityRule().check(path)
    assert any("classes" in v.message for v in violations)


def test_non_java_file_skipped(tmp_path: Path) -> None:
    path = _write(tmp_path, "foo.py", "class Foo: pass\n")
    assert JavaGranularityRule().check(path) == []


def test_six_public_methods_violates(tmp_path: Path) -> None:
    path = _write(tmp_path, "Foo.java", _SIX_METHODS)
    violations = JavaGranularityRule().check(path)
    assert any("6 public methods" in v.message for v in violations)


def test_three_args_method_violates(tmp_path: Path) -> None:
    path = _write(tmp_path, "Foo.java", _THREE_ARGS)
    violations = JavaGranularityRule().check(path)
    assert any("3 args" in v.message for v in violations)


def test_constructor_not_counted(tmp_path: Path) -> None:
    path = _write(tmp_path, "Foo.java", _CONSTRUCTOR_NOT_COUNTED)
    violations = JavaGranularityRule().check(path)
    assert not any("public methods" in v.message for v in violations)
