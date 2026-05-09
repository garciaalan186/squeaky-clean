"""Tests for GoImplementedClassParser."""

import pytest

from squeaky_clean.application.use_cases.implemented_class_parse_error import (
    ImplementedClassParseError,
)
from squeaky_clean.application.use_cases.parsers.go_implemented_class_parser import (
    GoImplementedClassParser,
)


def test_parses_struct() -> None:
    raw = "```go\npackage p\n\ntype EventId struct {\n    Value string\n}\n```"
    body = GoImplementedClassParser().parse(raw, "EventId")
    assert "type EventId struct" in body


def test_parses_interface() -> None:
    raw = "```go\npackage p\n\ntype Reader interface { Read() }\n```"
    body = GoImplementedClassParser().parse(raw, "Reader")
    assert "type Reader interface" in body


def test_parses_type_alias() -> None:
    raw = "```go\npackage p\n\ntype UserID = string\n```"
    body = GoImplementedClassParser().parse(raw, "UserID")
    assert "type UserID" in body


def test_strips_fence() -> None:
    raw = "```go\npackage p\n\ntype A struct{}\n```"
    body = GoImplementedClassParser().parse(raw, "A")
    assert "```" not in body


def test_raises_when_type_missing() -> None:
    raw = "```go\npackage p\n\ntype Other struct{}\n```"
    with pytest.raises(ImplementedClassParseError):
        GoImplementedClassParser().parse(raw, "EventId")


def test_case_sensitive() -> None:
    raw = "```go\npackage p\n\ntype eventid struct{}\n```"
    with pytest.raises(ImplementedClassParseError):
        GoImplementedClassParser().parse(raw, "EventId")
