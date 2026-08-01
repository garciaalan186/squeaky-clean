"""Tests for InvariantValueFabricator (extracted from InvariantTestRenderer)."""

from squeaky_clean.application.generation.testgen.invariant_value_fabricator import (
    InvariantValueFabricator,
)

_FIELDS = [("name", "str"), ("amount", "int")]


def test_violates_named_string_field_with_empty_literal() -> None:
    fab = InvariantValueFabricator("python")
    assert fab.args(_FIELDS, "name must not be empty") == '"", 0'


def test_numeric_field_goes_negative_for_lower_bound() -> None:
    fab = InvariantValueFabricator("python")
    assert fab.args(_FIELDS, "amount must be positive") == '"x", -1'


def test_upper_bound_is_overshot_by_one() -> None:
    fab = InvariantValueFabricator("python")
    assert fab.args(_FIELDS, "amount must be at most 100") == '"x", 101'


def test_length_limit_yields_repeat_expression_per_language() -> None:
    inv = "name length must be <= 3 chars"
    assert InvariantValueFabricator("python").args(_FIELDS, inv) == '"x" * 4, 0'
    assert InvariantValueFabricator("java").args(
        [("name", "String"), ("amount", "int")], inv,
    ) == '"x".repeat(4), 0'
    assert InvariantValueFabricator("typescript").args(_FIELDS, inv) \
        == "'x'.repeat(4), 0"


def test_java_map_default_uses_hashmap() -> None:
    fab = InvariantValueFabricator("java")
    fields = [("tags", "Map<String, String>"), ("amount", "int")]
    assert fab.args(fields, "amount must be positive") \
        == "new java.util.HashMap<String, String>(), -1"
