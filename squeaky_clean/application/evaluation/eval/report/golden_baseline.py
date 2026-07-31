"""golden_baseline: convert a shared GoldenMetrics into a ReplicateSummary."""

from __future__ import annotations

from squeaky_clean.application.evaluation.eval.sweep.replicate_summary import (
    ReplicateSummary,
)
from squeaky_clean.application.shared.problem.golden_metrics import GoldenMetrics


def to_replicate_summary(pid: str, g: GoldenMetrics) -> ReplicateSummary:
    """Adapt the DAG-safe golden VO to the detector's baseline type.

    GoldenMetrics lives in shared/ (ProblemSpec's component) and cannot
    import evaluation types; the conversion therefore lives here, on the
    evaluation side. Wall-clock/cache fields are not calibrated (they don't
    gate) and are zeroed.
    """
    return ReplicateSummary(
        problem_id=pid, replicates=g.replicates,
        tests_pass_mean=g.tests_pass_mean,
        tests_pass_stddev=g.tests_pass_stddev,
        functional_pass_mean=g.functional_pass_mean,
        functional_pass_stddev=g.functional_pass_stddev,
        security_pass_mean=g.security_pass_mean,
        security_pass_stddev=g.security_pass_stddev,
        cost_usd_mean=g.cost_usd_mean, cost_usd_stddev=g.cost_usd_stddev,
        wall_clock_ms_mean=0.0, wall_clock_ms_stddev=0.0,
        cache_hit_ratio=0.0,
    )
