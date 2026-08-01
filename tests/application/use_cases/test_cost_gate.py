"""Tests for CostGate."""

import pytest

from squeaky_clean.application.shared.gateways.cost_budget import CostBudget
from squeaky_clean.application.shared.gateways.cost_gate import BudgetExceededError, CostGate


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


def test_reserve_raises_when_projection_over() -> None:
    g = CostGate(CostBudget(max_cost_usd=5.0))
    g.record(4.0)
    with pytest.raises(BudgetExceededError):
        g.reserve(2.0)


def test_reserve_does_not_raise_when_under() -> None:
    g = CostGate(CostBudget(max_cost_usd=5.0))
    g.record(2.0)
    g.settle(g.reserve(2.5), 0.0)


def test_reserve_arithmetic_at_the_cap_boundary() -> None:
    g = CostGate(CostBudget(max_cost_usd=10.0))
    g.record(7.0)
    with pytest.raises(BudgetExceededError):
        g.reserve(3.5)
    g.settle(g.reserve(2.0), 0.0)   # under cap: allowed
    g.settle(g.reserve(3.0), 0.0)   # exactly at cap: allowed


def test_reserve_unlimited_never_raises() -> None:
    g = CostGate(CostBudget())
    g.record(1.0)
    g.settle(g.reserve(99999.0), 0.0)


def test_negative_record_clamped_to_zero() -> None:
    g = CostGate(CostBudget(max_cost_usd=10.0))
    g.record(-3.0)
    assert g.spent_usd() == 0.0


def test_default_constructor_uses_default_budget() -> None:
    g = CostGate()
    assert g.budget.is_unlimited()


def _budget(cap: float):
    from squeaky_clean.application.shared.gateways.cost_budget import CostBudget
    return CostBudget(max_cost_usd=cap)


def test_seed_carries_prior_spend() -> None:
    from squeaky_clean.application.shared.gateways.cost_gate import CostGate
    gate = CostGate(_budget(5.0))
    gate.seed(4.0)
    assert gate.spent_usd() == 4.0
    with pytest.raises(BudgetExceededError):
        gate.reserve(1.5)  # only $1 of headroom remains


def test_reserve_blocks_parallel_overshoot() -> None:
    """Concurrent reservers can never collectively exceed the cap."""
    import threading

    from squeaky_clean.application.shared.gateways.cost_gate import (
        BudgetExceededError,
        CostGate,
    )
    gate = CostGate(_budget(10.0))  # 10 slots of $1
    granted = []
    lock = threading.Lock()

    def worker() -> None:
        try:
            gate.reserve(1.0)
            with lock:
                granted.append(1)
        except BudgetExceededError:
            pass

    threads = [threading.Thread(target=worker) for _ in range(50)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    assert len(granted) == 10  # exactly cap/est, never more


def test_settle_reconciles_reservation() -> None:
    from squeaky_clean.application.shared.gateways.cost_gate import CostGate
    gate = CostGate(_budget(10.0))
    reserved = gate.reserve(5.0)
    gate.settle(reserved, 0.3)
    assert gate.spent_usd() == 0.3
    gate.settle(gate.reserve(9.0), 0.0)  # reservation freed: room for $9
