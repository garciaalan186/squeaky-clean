"""Tests for JavaImplementedClassParser."""

import pytest

from squeaky_clean.application.use_cases.implemented_class_parse_error import (
    ImplementedClassParseError,
)
from squeaky_clean.application.use_cases.parsers.java_implemented_class_parser import (
    JavaImplementedClassParser,
)


def test_parses_public_class() -> None:
    raw = "```java\npublic class Money { }\n```"
    body = JavaImplementedClassParser().parse(raw, "Money")
    assert "class Money" in body


def test_parses_public_interface() -> None:
    raw = "```java\npublic interface UserRepo { }\n```"
    body = JavaImplementedClassParser().parse(raw, "UserRepo")
    assert "interface UserRepo" in body


def test_parses_abstract_class_with_extends() -> None:
    raw = "```java\npublic abstract class Worker extends Base { }\n```"
    body = JavaImplementedClassParser().parse(raw, "Worker")
    assert "Worker" in body


def test_parses_enum() -> None:
    raw = "```java\npublic enum Status { OPEN, CLOSED }\n```"
    body = JavaImplementedClassParser().parse(raw, "Status")
    assert "enum Status" in body


def test_parses_class_no_modifier() -> None:
    raw = "```java\nclass Helper { }\n```"
    body = JavaImplementedClassParser().parse(raw, "Helper")
    assert "Helper" in body


def test_strips_fence() -> None:
    raw = "```java\npublic class A { }\n```"
    body = JavaImplementedClassParser().parse(raw, "A")
    assert "```" not in body


def test_raises_when_class_missing() -> None:
    raw = "```java\npublic class Other { }\n```"
    with pytest.raises(ImplementedClassParseError):
        JavaImplementedClassParser().parse(raw, "Wanted")


def test_case_sensitive() -> None:
    raw = "```java\npublic class money { }\n```"
    with pytest.raises(ImplementedClassParseError):
        JavaImplementedClassParser().parse(raw, "Money")
