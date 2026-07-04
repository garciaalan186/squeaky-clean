"""Tests for JavaScriptGranularityRule."""

from pathlib import Path

from squeaky_clean.domain.rules.javascript_granularity_rule import JavaScriptGranularityRule

_CLEAN = """export class Calculator {
  add(a, b) {
    return a + b;
  }
}
"""

_LONG = "\n".join([f"// line {i}" for i in range(90)])

_TWO_CLASSES = """export class Foo {}

export class Bar {}
"""


def _write(tmp: Path, name: str, body: str) -> Path:
    p = tmp / name
    p.write_text(body)
    return p


def test_clean_js_file_has_no_violations(tmp_path: Path) -> None:
    path = _write(tmp_path, "calculator.js", _CLEAN)
    assert JavaScriptGranularityRule().check(path) == []


def test_long_js_file_violates(tmp_path: Path) -> None:
    path = _write(tmp_path, "long.js", _LONG)
    violations = JavaScriptGranularityRule().check(path)
    assert any("lines" in v.message for v in violations)


def test_two_classes_js_file_violates(tmp_path: Path) -> None:
    path = _write(tmp_path, "two.js", _TWO_CLASSES)
    violations = JavaScriptGranularityRule().check(path)
    assert any("classes" in v.message for v in violations)


def test_non_js_file_skipped(tmp_path: Path) -> None:
    path = _write(tmp_path, "foo.py", "class Foo: pass\n")
    assert JavaScriptGranularityRule().check(path) == []


_SIX_METHODS = """export class Foo {
  constructor() {}
  a() { return 1; }
  b() { return 2; }
  c() { return 3; }
  d() { return 4; }
  e() { return 5; }
  f() { return 6; }
}
"""

_THREE_ARGS = """export class Foo {
  constructor() {}
  bar(a, b, c) { return a + b + c; }
}
"""

_DEFAULT_PARENS = """export class Foo {
  constructor() {}
  bar(a = (1, 2), b) { return a + b; }
}
"""

_PRIVATE_METHOD = """export class Foo {
  constructor() {}
  a() { return 1; }
  b() { return 2; }
  c() { return 3; }
  d() { return 4; }
  e() { return 5; }
  _helper() { return 0; }
}
"""

_CONSTRUCTOR_NOT_COUNTED = """export class Foo {
  constructor(a, b) {}
  m1() {}
  m2() {}
  m3() {}
}
"""


def test_six_public_methods_violates(tmp_path: Path) -> None:
    path = _write(tmp_path, "six.js", _SIX_METHODS)
    violations = JavaScriptGranularityRule().check(path)
    assert any("6 public methods" in v.message for v in violations)


def test_three_args_method_violates(tmp_path: Path) -> None:
    path = _write(tmp_path, "args.js", _THREE_ARGS)
    violations = JavaScriptGranularityRule().check(path)
    assert any("3 args" in v.message for v in violations)


def test_nested_parens_in_default_no_false_positive(tmp_path: Path) -> None:
    path = _write(tmp_path, "nested.js", _DEFAULT_PARENS)
    violations = JavaScriptGranularityRule().check(path)
    assert not any("args" in v.message for v in violations)


def test_private_method_not_counted(tmp_path: Path) -> None:
    path = _write(tmp_path, "priv.js", _PRIVATE_METHOD)
    violations = JavaScriptGranularityRule().check(path)
    assert not any("public methods" in v.message for v in violations)


def test_constructor_not_counted(tmp_path: Path) -> None:
    path = _write(tmp_path, "ctor.js", _CONSTRUCTOR_NOT_COUNTED)
    violations = JavaScriptGranularityRule().check(path)
    assert not any("public methods" in v.message for v in violations)
