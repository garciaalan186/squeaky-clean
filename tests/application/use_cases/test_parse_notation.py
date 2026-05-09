"""Tests for ParseNotation."""

import pytest

from squeaky_clean.application.use_cases.parse_notation import ParseNotation
from squeaky_clean.domain.entities.notation_parse_error import NotationParseError
from squeaky_clean.domain.value_objects.layer_type import LayerType

_PAYMENT = """MODULE Payment
LAYER Domain
EXPORTS [PaymentService, PaymentRepository]
DEPENDS [SharedKernel::Money, SharedKernel::Result]
CLASSES {
  PaymentService -> Facade {
    methods: [process(command: ProcessPaymentCommand): Result]
    depends: [PaymentProcessor, PaymentRepository]
  }
  PaymentProcessor -> Strategy {
    methods: [execute(payment: Payment): Result]
    concretes: [CreditCardProcessor, PayPalProcessor, CryptoProcessor]
  }
  PaymentRepository -> Repository {
    methods: [save(payment: Payment): void, find_by_id(id: PaymentId): Payment]
  }
  Payment -> Entity {
    methods: [validate(): Result]
  }
  PaymentId -> ValueObject {
    fields: [value: str]
    invariants: ["id must be non-empty"]
  }
  ProcessPaymentCommand -> ValueObject {}
}
INVARIANTS [
  "Payment amount must be positive",
  "Payment status transitions: Pending->Processing->Completed|Failed"
]
"""


def test_parse_payment_example() -> None:
    spec = ParseNotation().parse(_PAYMENT)
    assert spec.name == "Payment"
    assert spec.layer is LayerType.DOMAIN
    assert spec.exports == ("PaymentService", "PaymentRepository")
    assert spec.depends == ("SharedKernel::Money", "SharedKernel::Result")
    names = [c.name for c in spec.classes]
    assert names == [
        "PaymentService",
        "PaymentProcessor",
        "PaymentRepository",
        "Payment",
        "PaymentId",
        "ProcessPaymentCommand",
    ]
    by_name = {c.name: c for c in spec.classes}
    assert by_name["PaymentService"].pattern == "Facade"
    assert by_name["PaymentProcessor"].concretes == (
        "CreditCardProcessor",
        "PayPalProcessor",
        "CryptoProcessor",
    )
    assert by_name["PaymentRepository"].methods == (
        "save(payment: Payment): void",
        "find_by_id(id: PaymentId): Payment",
    )
    assert spec.invariants == (
        "Payment amount must be positive",
        "Payment status transitions: Pending->Processing->Completed|Failed",
    )
    assert by_name["PaymentId"].invariants == ("id must be non-empty",)
    assert by_name["ProcessPaymentCommand"].invariants == ()


def test_parse_malformed_raises() -> None:
    with pytest.raises(NotationParseError):
        ParseNotation().parse("MODULE Broken\nLAYER Nope\nCLASSES { Foo")
