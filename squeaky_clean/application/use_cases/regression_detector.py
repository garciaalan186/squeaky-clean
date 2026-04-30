"""RegressionDetector: flag metric drops >= 2 sigma vs a baseline summary."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from squeaky_clean.application.dtos.regression_record import RegressionRecord
from squeaky_clean.application.dtos.replicate_summary import ReplicateSummary

_DEFAULT_SIGMA_THRESHOLD: float = 2.0


@dataclass(frozen=True)
class _MetricView:
    metric: str
    baseline_mean: float
    baseline_stddev: float
    current_mean: float
    current_stddev: float


def _views(b: ReplicateSummary, c: ReplicateSummary) -> tuple[_MetricView, ...]:
    return (
        _MetricView("tests_pass", b.tests_pass_mean, b.tests_pass_stddev,
                    c.tests_pass_mean, c.tests_pass_stddev),
        _MetricView("functional_tests_pass",
                    b.functional_pass_mean, b.functional_pass_stddev,
                    c.functional_pass_mean, c.functional_pass_stddev),
        _MetricView("security_tests_pass",
                    b.security_pass_mean, b.security_pass_stddev,
                    c.security_pass_mean, c.security_pass_stddev),
    )


class RegressionDetector:
    """Compare two ReplicateSummary objects and emit RegressionRecord list."""

    def __init__(self, sigma_threshold: float = _DEFAULT_SIGMA_THRESHOLD) -> None:
        self._sigma: float = sigma_threshold

    def detect(
        self,
        baseline: ReplicateSummary,
        current: ReplicateSummary,
        timestamp: str,
    ) -> Sequence[RegressionRecord]:
        """Return the regressions where current_mean < baseline_mean - 2sigma."""
        if baseline.problem_id != current.problem_id:
            return ()
        out: list[RegressionRecord] = []
        for v in _views(baseline, current):
            sigma = max(v.baseline_stddev, 1e-9)
            drop = (v.baseline_mean - v.current_mean) / sigma
            if drop >= self._sigma:
                out.append(RegressionRecord(
                    metric=v.metric, problem_id=baseline.problem_id,
                    baseline_mean=v.baseline_mean,
                    baseline_stddev=v.baseline_stddev,
                    current_mean=v.current_mean,
                    current_stddev=v.current_stddev,
                    sigma_drop=drop, timestamp=timestamp,
                ))
        return tuple(out)
