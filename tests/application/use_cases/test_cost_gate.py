"""Tests for CostGate."""

import pytest

from squeaky_clean.application.dtos.cost_budget import CostBudget
from squeaky_clean.application.use_cases.cost_gate import BudgetExceededError, CostGate


def test_unlimited_budget_never_raises() -> None:
    g = CostGate(CostBudget())
    g.record(1_000_000.0)
    assert g.spent_usd() == 1_000_000.0


def test_under_cap_records() -> None:
    g = CostGate(CostBudget(max_cost_usd=10.0))
    g.record(2.0)
    g.record(3.0)
    assert g.spent_usd() == 5.0


def test_over_cap_raises() -> None:
    g = CostGate(CostBudget(max_cost_usd=5.0))
    g.record(4.0)
    with pytest.raises(BudgetExceededError):
        g.record(2.0)


def test_check_raises_when_projection_over() -> None:
    g = CostGate(CostBudget(max_cost_usd=5.0))
    g.record(4.0)
    with pytest.raises(BudgetExceededError):
        g.check(2.0)


def test_check_does_not_raise_when_under() -> None:
    g = CostGate(CostBudget(max_cost_usd=5.0))
    g.record(2.0)
    g.check(2.5)


def test_would_exceed_arithmetic() -> None:
    g = CostGate(CostBudget(max_cost_usd=10.0))
    g.record(7.0)
    assert g.would_exceed(3.5) is True
    assert g.would_exceed(2.0) is False
    assert g.would_exceed(3.0) is False


def test_would_exceed_unlimited_is_false() -> None:
    g = CostGate(CostBudget())
    g.record(1.0)
    assert g.would_exceed(99999.0) is False


def test_negative_record_clamped_to_zero() -> None:
    g = CostGate(CostBudget(max_cost_usd=10.0))
    g.record(-3.0)
    assert g.spent_usd() == 0.0


def test_default_constructor_uses_default_budget() -> None:
    g = CostGate()
    assert g.budget().is_unlimited()
