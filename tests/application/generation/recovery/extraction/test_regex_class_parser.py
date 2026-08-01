"""Tests for RegexClassParser: slicing source into ClassRecords via regexes."""

import re

from squeaky_clean.application.generation.recovery.extraction.regex_class_parser import (
    RegexClassParser,
)

_CLASS = re.compile(
    r"^class\s+(?P<name>\w+)(?:\s+extends\s+(?P<base>[\w.]+))?"
    r"(?:\s+implements\s+(?P<impl>[\w, ]+))?",
    re.MULTILINE,
)
_METHOD = re.compile(r"^[ \t]+(?P<name>\w+)\s*\((?P<args>[^)]*)\)\s*\{", re.MULTILINE)
_FIELD = re.compile(r"^[ \t]+(?P<name>\w+)\s*:\s*(?P<type>\w+);", re.MULTILINE)

_SOURCE = (
    "@Component\n"
    "class User extends Base implements Serializable, Comparable\n"
    "  id: str;\n"
    "  rename(name) {\n"
    "  if (flag) {\n"
    "class Order\n"
    "  total() {\n"
)


def _parser() -> RegexClassParser:
    return RegexClassParser(_CLASS, _METHOD, _FIELD)


def test_bodies_slice_at_the_next_class_declaration() -> None:
    user, order = _parser().parse(_SOURCE, lambda name: name, ())
    assert user.methods == ("rename(name)",)
    assert user.fields == ("id: str",)
    assert order.methods == ("total()",)
    assert order.fields == ()


def test_bases_combine_extends_and_split_implements_clauses() -> None:
    user, order = _parser().parse(_SOURCE, lambda name: name, ())
    assert user.bases == ("Base", "Serializable", "Comparable")
    assert order.bases == ()


def test_language_keywords_are_never_reported_as_methods() -> None:
    source = "class Loop\n  while (x) {\n  for (y) {\n  run() {\n"
    (record,) = _parser().parse(source, lambda name: name, ())
    assert record.methods == ("run()",)


def test_fqn_imports_and_leading_decorators_flow_into_each_record() -> None:
    user, order = _parser().parse(_SOURCE, lambda name: f"app.{name}", ("os", "re"))
    assert (user.fqn, order.fqn) == ("app.User", "app.Order")
    assert user.imports == ("os", "re") and order.imports == ("os", "re")
    assert user.decorators == ("Component",)
