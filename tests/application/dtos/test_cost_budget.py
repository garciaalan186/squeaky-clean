"""Tests for the CostBudget DTO."""

import pytest

from squeaky_clean.application.dtos.cost_budget import CostBudget


def test_default_is_unlimited() -> None:
    b = CostBudget()
    assert b.is_unlimited()
    assert b.warn_threshold_usd() is None


def test_explicit_cap_with_warn() -> None:
    b = CostBudget(max_cost_usd=10.0, warn_at_pct=0.5)
    assert not b.is_unlimited()
    assert b.warn_threshold_usd() == 5.0


def test_warn_pct_zero_rejected() -> None:
    with pytest.raises(ValueError):
        CostBudget(max_cost_usd=10.0, warn_at_pct=0.0)


def test_warn_pct_above_one_rejected() -> None:
    with pytest.raises(ValueError):
        CostBudget(max_cost_usd=10.0, warn_at_pct=1.5)


def test_negative_cap_rejected() -> None:
    with pytest.raises(ValueError):
        CostBudget(max_cost_usd=-1.0)
