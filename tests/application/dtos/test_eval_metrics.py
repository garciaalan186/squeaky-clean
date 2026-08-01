"""Tests for EvalMetrics (frozen aggregate, R6.3)."""

import dataclasses

import pytest

from squeaky_clean.domain.entities.eval_metrics import EvalMetrics
from squeaky_clean.domain.value_objects.metrics.cost_breakdown import CostBreakdown
from squeaky_clean.domain.value_objects.metrics.test_outcome import TestOutcome


def test_empty_returns_zero_initialized_instance() -> None:
    m = EvalMetrics.empty()
    assert m.tests_pass == 0.0
    assert m.cost.total_tokens_input == 0
    assert m.structure.classes_per_module == ()
    assert m.estimated_cost_usd == 0.0


def test_empty_instances_are_independent() -> None:
    a = EvalMetrics.empty()
    b = EvalMetrics.empty()
    a.cache_by_tier.clear()
    a.cache_by_tier.update({})
    assert a.cache_by_tier is not b.cache_by_tier


def test_is_frozen() -> None:
    m = EvalMetrics.empty()
    with pytest.raises(dataclasses.FrozenInstanceError):
        m.architecture_violations = 1  # type: ignore[misc]


def test_property_passthroughs_reach_nested_values() -> None:
    m = EvalMetrics(
        test_outcome=TestOutcome(
            tests_pass=0.5, functional_tests_pass=0.75,
            security_tests_pass=0.25,
        ),
        cost=CostBreakdown(estimated_cost_usd=1.5),
    )
    assert m.tests_pass == 0.5
    assert m.functional_tests_pass == 0.75
    assert m.security_tests_pass == 0.25
    assert m.estimated_cost_usd == 1.5
