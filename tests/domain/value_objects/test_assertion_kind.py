"""Tests for AssertionKind enum."""

from squeaky_clean.domain.value_objects.assertion_kind import AssertionKind


def test_members_and_values() -> None:
    assert {k.value for k in AssertionKind} == {
        "raises", "equals", "field_holds", "call_only",
    }


def test_call_only_is_the_floor_kind() -> None:
    assert AssertionKind("call_only") is AssertionKind.CALL_ONLY
