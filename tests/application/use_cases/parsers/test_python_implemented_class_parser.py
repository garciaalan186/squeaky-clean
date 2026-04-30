"""Tests for PythonImplementedClassParser."""

import pytest

from squeaky_clean.application.use_cases.implemented_class_parse_error import (
    ImplementedClassParseError,
)
from squeaky_clean.application.use_cases.parsers.python_implemented_class_parser import (
    PythonImplementedClassParser,
)


def test_parses_class_with_decorator() -> None:
    raw = "```python\n@dataclass(frozen=True)\nclass Money:\n    amount: int\n```"
    body = PythonImplementedClassParser().parse(raw, "Money")
    assert "class Money:" in body


def test_parses_class_with_base() -> None:
    raw = "```python\nclass UserRepo(Repository):\n    pass\n```"
    body = PythonImplementedClassParser().parse(raw, "UserRepo")
    assert "class UserRepo" in body


def test_strips_fence() -> None:
    raw = "```python\nclass Money:\n    pass\n```"
    body = PythonImplementedClassParser().parse(raw, "Money")
    assert "```" not in body


def test_raises_when_class_missing() -> None:
    raw = "```python\ndef helper(): pass\n```"
    with pytest.raises(ImplementedClassParseError):
        PythonImplementedClassParser().parse(raw, "Money")


def test_case_sensitive() -> None:
    raw = "```python\nclass money:\n    pass\n```"
    with pytest.raises(ImplementedClassParseError):
        PythonImplementedClassParser().parse(raw, "Money")
