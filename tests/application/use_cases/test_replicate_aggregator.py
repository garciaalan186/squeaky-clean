"""Unit tests for ReplicateAggregator."""

import math

from squeaky_clean.application.evaluation.eval.sweep.replicate_aggregator import ReplicateAggregator
from squeaky_clean.domain.entities.eval_metrics import EvalMetrics
from squeaky_clean.domain.value_objects.metrics.cost_breakdown import CostBreakdown
from squeaky_clean.domain.value_objects.metrics.test_outcome import TestOutcome


def _metrics(tests_pass: float, cost: float, hit: int, miss: int) -> EvalMetrics:
    return EvalMetrics(
        test_outcome=TestOutcome(
            tests_pass=tests_pass, functional_tests_pass=tests_pass,
            security_tests_pass=tests_pass,
        ),
        cost=CostBreakdown(estimated_cost_usd=cost),
        total_wall_clock_ms=1000,
        cache_hit_count=hit,
        cache_miss_count=miss,
    )


def test_empty_replicates_returns_zero_summary() -> None:
    summary = ReplicateAggregator().aggregate("P0", [])
    assert summary.replicates == 0
    assert summary.tests_pass_mean == 0.0
    assert summary.cache_hit_ratio == 0.0


def test_single_replicate_has_zero_stddev() -> None:
    summary = ReplicateAggregator().aggregate("P0", [_metrics(0.8, 0.5, 0, 1)])
    assert summary.replicates == 1
    assert summary.tests_pass_mean == 0.8
    assert summary.tests_pass_stddev == 0.0


def test_three_replicates_computes_mean_and_stddev() -> None:
    rs = [_metrics(1.0, 0.5, 0, 1), _metrics(0.5, 0.3, 0, 1), _metrics(0.0, 0.7, 0, 1)]
    summary = ReplicateAggregator().aggregate("P0", rs)
    assert summary.replicates == 3
    assert summary.tests_pass_mean == 0.5
    assert math.isclose(summary.tests_pass_stddev, 0.5, rel_tol=1e-6)


def test_cache_hit_ratio() -> None:
    rs = [_metrics(1.0, 0.0, 4, 1), _metrics(1.0, 0.0, 3, 2)]
    summary = ReplicateAggregator().aggregate("P0", rs)
    assert summary.cache_hit_ratio == 0.7
