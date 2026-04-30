"""Tests for PatternName literal and ALL_PATTERNS."""

from squeaky_clean.domain.value_objects.pattern_name import ALL_PATTERNS


def test_all_patterns_has_thirty_four_entries() -> None:
    assert len(ALL_PATTERNS) == 34


def test_all_patterns_contains_simple_class() -> None:
    assert "SimpleClass" in ALL_PATTERNS


def test_all_patterns_contains_value_object() -> None:
    assert "ValueObject" in ALL_PATTERNS
