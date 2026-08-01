"""Tests for NotationFieldParser key/value extraction."""

from squeaky_clean.application.generation.notation.notation_field_parser import (
    NotationFieldParser,
)


def test_parses_scalar_and_bracketed_values() -> None:
    # Bracketed values come back as their INNER text (brackets stripped).
    body = "implements: PaymentPort\nmethods: [pay(a: Money): Result]\n"
    fields = NotationFieldParser().parse(body)
    assert fields["implements"] == "PaymentPort"
    assert fields["methods"] == "pay(a: Money): Result"


def test_bracket_value_may_contain_commas_and_newlines() -> None:
    body = "depends: [A,\n  B, C]\nfields: [id: Id]"
    fields = NotationFieldParser().parse(body)
    assert fields["depends"].replace("\n", " ").split() == "A, B, C".split()
    assert fields["fields"] == "id: Id"


def test_empty_body_gives_empty_dict() -> None:
    assert NotationFieldParser().parse("") == {}
