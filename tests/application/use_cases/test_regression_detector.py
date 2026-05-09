"""Unit tests for RegressionDetector."""

from squeaky_clean.application.dtos.replicate_summary import ReplicateSummary
from squeaky_clean.application.use_cases.regression_detector import RegressionDetector


def _summary(
    pid: str, mean: float, stddev: float = 0.05,
) -> ReplicateSummary:
    return ReplicateSummary(
        problem_id=pid, replicates=3,
        tests_pass_mean=mean, tests_pass_stddev=stddev,
        functional_pass_mean=mean, functional_pass_stddev=stddev,
        security_pass_mean=mean, security_pass_stddev=stddev,
        cost_usd_mean=1.0, cost_usd_stddev=0.1,
        wall_clock_ms_mean=1000.0, wall_clock_ms_stddev=10.0,
        cache_hit_ratio=0.0,
    )


def test_no_regression_when_means_close() -> None:
    a = _summary("P0", 0.95)
    b = _summary("P0", 0.94)
    out = RegressionDetector().detect(a, b, "2026-04-25")
    assert out == ()


def test_regression_detected_at_2sigma() -> None:
    a = _summary("P0", 1.00, 0.05)
    b = _summary("P0", 0.85, 0.05)
    out = RegressionDetector().detect(a, b, "2026-04-25")
    assert len(out) == 3
    assert all(r.sigma_drop >= 2.0 for r in out)


def test_mismatched_problem_ids_no_records() -> None:
    a = _summary("P0", 1.0)
    b = _summary("P1", 0.0)
    assert RegressionDetector().detect(a, b, "ts") == ()


def test_zero_stddev_still_detects_with_min_sigma() -> None:
    a = _summary("P0", 1.0, 0.0)
    b = _summary("P0", 0.5, 0.0)
    out = RegressionDetector().detect(a, b, "ts")
    assert len(out) == 3
