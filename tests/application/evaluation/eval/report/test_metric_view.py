"""Tests for MetricView + metric_views over ReplicateSummary pairs."""

from squeaky_clean.application.evaluation.eval.report.metric_view import (
    MetricView,
    metric_views,
)
from squeaky_clean.application.evaluation.eval.sweep.replicate_summary import ReplicateSummary


def _summary(mean: float, stddev: float) -> ReplicateSummary:
    return ReplicateSummary(
        problem_id="P0", replicates=3,
        tests_pass_mean=mean, tests_pass_stddev=stddev,
        functional_pass_mean=mean, functional_pass_stddev=stddev,
        security_pass_mean=mean, security_pass_stddev=stddev,
        cost_usd_mean=1.0, cost_usd_stddev=0.1,
        wall_clock_ms_mean=1000.0, wall_clock_ms_stddev=10.0,
        cache_hit_ratio=0.0,
    )


def test_metric_views_covers_the_three_gated_metrics() -> None:
    views = metric_views(_summary(1.0, 0.1), _summary(0.5, 0.2))
    assert [v.metric for v in views] == [
        "tests_pass", "functional_tests_pass", "security_tests_pass",
    ]
    assert all(v.baseline_mean == 1.0 for v in views)
    assert all(v.current_mean == 0.5 for v in views)


def test_metric_view_carries_stddevs() -> None:
    v = MetricView("tests_pass", 1.0, 0.1, 0.5, 0.2)
    assert v.baseline_stddev == 0.1
    assert v.current_stddev == 0.2
