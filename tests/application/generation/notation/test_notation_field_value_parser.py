"""Tests for NotationFieldValueParser kind dispatch."""

import pytest

from squeaky_clean.application.generation.notation.notation_field_value_parser import (
    NotationFieldValueParser,
)


def test_name_list_splits_plain_items() -> None:
    parser = NotationFieldValueParser()
    assert parser.sequence("[A, B, C]", "name_list") == ("A", "B", "C")


def test_method_list_honors_commas_inside_parens() -> None:
    parser = NotationFieldValueParser()
    raw = "[pay(a: Money, b: Money): Result, refund(): void]"
    assert parser.sequence(raw, "method_list") == (
        "pay(a: Money, b: Money): Result",
        "refund(): void",
    )


def test_invariant_list_strips_quotes() -> None:
    parser = NotationFieldValueParser()
    raw = '["amount positive", "status is Pending"]'
    assert parser.sequence(raw, "invariant_list") == (
        "amount positive",
        "status is Pending",
    )


def test_empty_body_yields_empty_tuple() -> None:
    parser = NotationFieldValueParser()
    assert parser.sequence("", "name_list") == ()


def test_non_sequence_kind_is_a_caller_bug() -> None:
    parser = NotationFieldValueParser()
    with pytest.raises(ValueError, match="not a sequence kind"):
        parser.sequence("Foo", "scalar")
