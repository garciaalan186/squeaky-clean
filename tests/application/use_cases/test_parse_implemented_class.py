"""Tests for ParseImplementedClass."""

import pytest

from squeaky_clean.application.use_cases.implemented_class_parse_error import (
    ImplementedClassParseError,
)
from squeaky_clean.application.use_cases.parse_implemented_class import ParseImplementedClass

_CANNED = '''Here is the implementation:
```python
"""Operand value object."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Operand:
    value: int
```
'''


def test_parse_extracts_fenced_body() -> None:
    parser = ParseImplementedClass()
    body = parser.parse(_CANNED, "Operand")
    assert "class Operand" in body
    assert "```" not in body
    assert body.startswith('"""Operand value object."""')


def test_parse_raises_when_no_python_fence() -> None:
    parser = ParseImplementedClass()
    with pytest.raises(ImplementedClassParseError):
        parser.parse("no fence here", "Operand")


def test_parse_extracts_javascript_body() -> None:
    from squeaky_clean.application.use_cases.parsers.javascript_implemented_class_parser import (
        JavaScriptImplementedClassParser,
    )
    raw = (
        "Here is the implementation:\n"
        "```javascript\n"
        "export class Operand {\n"
        "  constructor(value) { this.value = value; }\n"
        "}\n"
        "```\n"
    )
    body = ParseImplementedClass(JavaScriptImplementedClassParser()).parse(
        raw, "Operand",
    )
    assert "class Operand" in body
    assert "export class" in body


def test_parse_raises_when_unclosed_fence() -> None:
    parser = ParseImplementedClass()
    raw = "```python\nclass Operand: pass\n"
    with pytest.raises(ImplementedClassParseError):
        parser.parse(raw, "Operand")


def test_parse_extracts_java_interface() -> None:
    from squeaky_clean.application.use_cases.parsers.java_implemented_class_parser import (
        JavaImplementedClassParser,
    )
    raw = (
        "```java\n"
        "public interface DiscountStrategy {\n"
        "    double apply(double price);\n"
        "}\n"
        "```\n"
    )
    body = ParseImplementedClass(JavaImplementedClassParser()).parse(
        raw, "DiscountStrategy",
    )
    assert "interface DiscountStrategy" in body


def test_parse_raises_when_class_missing() -> None:
    parser = ParseImplementedClass()
    raw = "```python\nclass Other: pass\n```"
    with pytest.raises(ImplementedClassParseError):
        parser.parse(raw, "Operand")
