"""Tests for JavaScriptImplementedClassParser."""

import pytest

from squeaky_clean.application.use_cases.implemented_class_parse_error import (
    ImplementedClassParseError,
)
from squeaky_clean.application.use_cases.parsers.javascript_implemented_class_parser import (
    JavaScriptImplementedClassParser,
)


def test_parses_class() -> None:
    raw = "```javascript\nclass Money {}\n```"
    body = JavaScriptImplementedClassParser().parse(raw, "Money")
    assert "class Money" in body


def test_parses_export_class() -> None:
    raw = "```javascript\nexport class Money {}\n```"
    body = JavaScriptImplementedClassParser().parse(raw, "Money")
    assert "Money" in body


def test_parses_export_default_class() -> None:
    raw = "```javascript\nexport default class Money {}\n```"
    body = JavaScriptImplementedClassParser().parse(raw, "Money")
    assert "Money" in body


def test_parses_function() -> None:
    raw = "```javascript\nfunction makeMoney() { return {}; }\n```"
    body = JavaScriptImplementedClassParser().parse(raw, "makeMoney")
    assert "makeMoney" in body


def test_parses_typescript_interface() -> None:
    raw = "```typescript\nexport interface Money { value: number }\n```"
    body = JavaScriptImplementedClassParser().parse(raw, "Money")
    assert "Money" in body


def test_strips_fence() -> None:
    raw = "```javascript\nclass A {}\n```"
    body = JavaScriptImplementedClassParser().parse(raw, "A")
    assert "```" not in body


def test_raises_when_class_missing() -> None:
    raw = "```javascript\nclass Other {}\n```"
    with pytest.raises(ImplementedClassParseError):
        JavaScriptImplementedClassParser().parse(raw, "Money")


def test_case_sensitive() -> None:
    raw = "```javascript\nclass money {}\n```"
    with pytest.raises(ImplementedClassParseError):
        JavaScriptImplementedClassParser().parse(raw, "Money")
