"""Tests for EvalMetrics."""

from squeaky_clean.application.dtos.eval_metrics import EvalMetrics


def test_empty_returns_zero_initialized_instance() -> None:
    m = EvalMetrics.empty()
    assert m.tests_pass == 0.0
    assert m.total_tokens_input == 0
    assert m.classes_per_module == []
    assert m.estimated_cost_usd == 0.0


def test_empty_instances_are_independent() -> None:
    a = EvalMetrics.empty()
    b = EvalMetrics.empty()
    a.classes_per_module.append(3)
    assert b.classes_per_module == []
