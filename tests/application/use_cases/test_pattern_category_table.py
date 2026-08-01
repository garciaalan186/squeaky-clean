"""Tests for pattern_category_table (catalog completeness + fallback)."""

from typing import get_args

from squeaky_clean.application.generation.emission.routing.pattern_category_table import (
    FALLBACK_CATEGORY,
    FALLBACK_NAME,
    PATTERN_CATEGORY,
)
from squeaky_clean.domain.value_objects.pattern_name import PatternName


def test_every_pattern_name_literal_has_a_category() -> None:
    assert set(PATTERN_CATEGORY) == set(get_args(PatternName))


def test_categories_are_the_four_emitter_directories() -> None:
    assert set(PATTERN_CATEGORY.values()) == {
        "creational", "structural", "behavioral", "ddd_clean",
    }


def test_fallback_is_the_simple_class_escape_hatch() -> None:
    assert FALLBACK_NAME == "SimpleClassEmitter"
    assert FALLBACK_CATEGORY == "ddd_clean"
