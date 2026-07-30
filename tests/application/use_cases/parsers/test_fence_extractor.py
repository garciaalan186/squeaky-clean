"""Tests for FenceExtractor."""

import pytest

from squeaky_clean.application.generation.emission.parsers.fence_extractor import FenceExtractor
from squeaky_clean.application.generation.emission.parsers.implemented_class_parse_error import (
    ImplementedClassParseError,
)


def test_extracts_first_fence_body() -> None:
    raw = "Here:\n```python\nclass A: pass\n```\nrest"
    body = FenceExtractor().extract(raw, "A")
    assert "class A: pass" in body
    assert "```" not in body


def test_raises_on_missing_fence() -> None:
    with pytest.raises(ImplementedClassParseError):
        FenceExtractor().extract("no fence", "A")


def test_raises_on_unclosed_fence() -> None:
    with pytest.raises(ImplementedClassParseError):
        FenceExtractor().extract("```python\nclass A: pass\n", "A")


def test_prefers_fence_that_defines_the_target_class() -> None:
    # An explanatory fence precedes the real class fence — pick the real one.
    raw = (
        "Example usage:\n```python\nx = Widget()\n```\n"
        "Implementation:\n```python\nclass Widget:\n    pass\n```\n"
    )
    body = FenceExtractor().extract(raw, "Widget")
    assert "class Widget" in body
    assert "x = Widget()" not in body


def test_falls_back_to_first_fence_when_class_absent() -> None:
    raw = "```python\nfirst = 1\n```\n```python\nsecond = 2\n```"
    body = FenceExtractor().extract(raw, "Missing")
    assert body == "first = 1"
