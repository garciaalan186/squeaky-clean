"""Tests for NotationInvariantsParser quoted-string extraction."""

from squeaky_clean.application.generation.notation.notation_invariants_parser import (
    NotationInvariantsParser,
)


def test_extracts_quoted_strings() -> None:
    raw = '["Payment amount must be positive", "Status: Pending->Done"]'
    assert NotationInvariantsParser().parse(raw) == (
        "Payment amount must be positive",
        "Status: Pending->Done",
    )


def test_commas_inside_quotes_do_not_split() -> None:
    raw = '["a, b, and c stay together"]'
    assert NotationInvariantsParser().parse(raw) == ("a, b, and c stay together",)


def test_empty_body_yields_empty_tuple() -> None:
    assert NotationInvariantsParser().parse("[]") == ()
    assert NotationInvariantsParser().parse("") == ()
