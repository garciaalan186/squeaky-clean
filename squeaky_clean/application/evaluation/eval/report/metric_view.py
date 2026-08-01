"""MetricView: baseline-vs-current stats for one regression-gated metric."""

from __future__ import annotations

from dataclasses import dataclass

from squeaky_clean.application.evaluation.eval.sweep.replicate_summary import ReplicateSummary


@dataclass(frozen=True)
class MetricView:
    """One metric's baseline and current mean/stddev pair."""

    metric: str
    baseline_mean: float
    baseline_stddev: float
    current_mean: float
    current_stddev: float


def metric_views(
    baseline: ReplicateSummary, current: ReplicateSummary,
) -> tuple[MetricView, ...]:
    """Return the gated metric views (tests / functional / security pass)."""
    return (
        MetricView("tests_pass",
                   baseline.tests_pass_mean, baseline.tests_pass_stddev,
                   current.tests_pass_mean, current.tests_pass_stddev),
        MetricView("functional_tests_pass",
                   baseline.functional_pass_mean, baseline.functional_pass_stddev,
                   current.functional_pass_mean, current.functional_pass_stddev),
        MetricView("security_tests_pass",
                   baseline.security_pass_mean, baseline.security_pass_stddev,
                   current.security_pass_mean, current.security_pass_stddev),
    )
