"""Tests for NotationClassParser CLASSES-body parsing."""

import pytest

from squeaky_clean.application.generation.notation.notation_class_parser import (
    NotationClassParser,
)
from squeaky_clean.domain.entities.notation_parse_error import NotationParseError

_BODY = """
Payment -> Entity {
  fields: [id: PaymentId, amount: Money]
  methods: [validate(): Result]
  invariants: ["amount positive"]
}
Processor -> Strategy {
  methods: [execute(payment: Payment): Result]
  concretes: [CardProcessor, CryptoProcessor]
}
"""


def test_parses_every_declared_field_kind() -> None:
    payment, processor = NotationClassParser().parse(_BODY)
    assert payment.name == "Payment"
    assert payment.pattern == "Entity"
    assert payment.fields == ("id: PaymentId", "amount: Money")
    assert payment.methods == ("validate(): Result",)
    assert payment.invariants == ("amount positive",)
    assert processor.concretes == ("CardProcessor", "CryptoProcessor")
    assert processor.implements is None


def test_header_without_arrow_raises() -> None:
    with pytest.raises(NotationParseError, match="missing '->'"):
        NotationClassParser().parse("Payment Entity {}")


def test_unknown_pattern_raises() -> None:
    with pytest.raises(NotationParseError, match="unknown pattern"):
        NotationClassParser().parse("Payment -> Blob {}")
