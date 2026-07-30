"""Tests for BudgetExceededError (R2.4 extraction)."""

from squeaky_clean.application.shared.gateways.budget_exceeded_error import (
    BudgetExceededError,
)
from squeaky_clean.application.shared.gateways.cost_gate import (
    BudgetExceededError as ReExported,
)


def test_is_runtime_error() -> None:
    assert issubclass(BudgetExceededError, RuntimeError)


def test_cost_gate_reexports_the_same_class() -> None:
    # Back-compat: `from cost_gate import BudgetExceededError` still resolves.
    assert ReExported is BudgetExceededError
