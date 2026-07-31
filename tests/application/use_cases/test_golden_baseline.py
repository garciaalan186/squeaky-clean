"""Tests for golden_baseline conversion (R5.2)."""

from squeaky_clean.application.evaluation.eval.report.golden_baseline import (
    to_replicate_summary,
)
from squeaky_clean.application.shared.problem.golden_metrics import GoldenMetrics


def test_conversion_maps_all_calibrated_fields() -> None:
    golden = GoldenMetrics(
        replicates=3,
        tests_pass_mean=1.0, tests_pass_stddev=0.05,
        functional_pass_mean=0.9, functional_pass_stddev=0.04,
        security_pass_mean=0.5, security_pass_stddev=0.1,
        cost_usd_mean=0.05, cost_usd_stddev=0.01,
    )
    s = to_replicate_summary("P2", golden)
    assert s.problem_id == "P2" and s.replicates == 3
    assert s.tests_pass_mean == 1.0 and s.tests_pass_stddev == 0.05
    assert s.functional_pass_mean == 0.9 and s.security_pass_stddev == 0.1
    assert s.cost_usd_mean == 0.05


def test_uncalibrated_fields_are_zeroed() -> None:
    golden = GoldenMetrics(
        replicates=3,
        tests_pass_mean=1.0, tests_pass_stddev=0.0,
        functional_pass_mean=1.0, functional_pass_stddev=0.0,
        security_pass_mean=0.0, security_pass_stddev=0.0,
        cost_usd_mean=0.05, cost_usd_stddev=0.01,
    )
    s = to_replicate_summary("P2", golden)
    assert s.wall_clock_ms_mean == 0.0 and s.cache_hit_ratio == 0.0
