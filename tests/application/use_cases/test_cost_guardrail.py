"""Unit tests for CostGuardrail."""

import pytest

from squeaky_clean.application.use_cases.cost_guardrail import (
    CostExceededError,
    CostGuardrail,
)


def test_under_cap_does_not_raise() -> None:
    g = CostGuardrail(max_usd=10.0)
    g.add(2.5)
    g.add(3.0)
    assert g.spent() == 5.5
    assert g.remaining() == 4.5


def test_at_cap_does_not_raise() -> None:
    g = CostGuardrail(max_usd=5.0)
    g.add(5.0)
    assert g.spent() == 5.0


def test_over_cap_raises() -> None:
    g = CostGuardrail(max_usd=5.0)
    g.add(4.0)
    with pytest.raises(CostExceededError):
        g.add(2.0)


def test_zero_cap_disables_guardrail() -> None:
    g = CostGuardrail(max_usd=0.0)
    g.add(1000000.0)
    assert g.spent() == 1000000.0


def test_negative_delta_clamped_to_zero() -> None:
    g = CostGuardrail(max_usd=10.0)
    g.add(-5.0)
    assert g.spent() == 0.0
