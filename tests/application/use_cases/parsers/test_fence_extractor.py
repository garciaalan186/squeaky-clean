"""Tests for FenceExtractor."""

import pytest

from squeaky_clean.application.use_cases.implemented_class_parse_error import (
    ImplementedClassParseError,
)
from squeaky_clean.application.use_cases.parsers.fence_extractor import FenceExtractor


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
