"""Tests for the CostBreakdown value object."""

import dataclasses

import pytest

from squeaky_clean.application.evaluation.eval.metrics.model.cost_breakdown import CostBreakdown


def test_defaults_are_zero() -> None:
    c = CostBreakdown()
    assert c.estimated_cost_usd == 0.0
    assert c.total_tokens_input == 0
    assert c.total_tokens_output == 0
    assert c.icp_wall_duration_ms == 0


def test_is_frozen() -> None:
    c = CostBreakdown()
    with pytest.raises(dataclasses.FrozenInstanceError):
        c.estimated_cost_usd = 1.0  # type: ignore[misc]


def test_holds_per_tier_values() -> None:
    c = CostBreakdown(
        estimated_cost_usd=0.42,
        architect_input_tokens=100, architect_output_tokens=50,
        icp_cost_usd=0.1, security_architect_duration_ms=250,
    )
    assert c.estimated_cost_usd == pytest.approx(0.42)
    assert c.architect_input_tokens == 100
    assert c.security_architect_duration_ms == 250
