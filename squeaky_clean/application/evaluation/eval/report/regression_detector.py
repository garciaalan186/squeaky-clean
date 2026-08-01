"""RegressionDetector: flag metric drops >= 2 sigma vs a baseline summary."""

from __future__ import annotations

from collections.abc import Sequence

from squeaky_clean.application.evaluation.eval.report.metric_view import metric_views
from squeaky_clean.application.evaluation.eval.report.regression_record import RegressionRecord
from squeaky_clean.application.evaluation.eval.sweep.replicate_summary import ReplicateSummary

_DEFAULT_SIGMA_THRESHOLD: float = 2.0


class RegressionDetector:
    """Compare two ReplicateSummary objects and emit RegressionRecord list.

    The report ``timestamp`` is fixed at construction so ``detect`` keeps
    to the 2-argument granularity bound.
    """

    def __init__(
        self, timestamp: str, sigma_threshold: float = _DEFAULT_SIGMA_THRESHOLD,
    ) -> None:
        self._timestamp: str = timestamp
        self._sigma: float = sigma_threshold

    def detect(
        self, baseline: ReplicateSummary, current: ReplicateSummary,
    ) -> Sequence[RegressionRecord]:
        """Return the regressions where current_mean < baseline_mean - 2sigma."""
        if baseline.problem_id != current.problem_id:
            return ()
        out: list[RegressionRecord] = []
        for v in metric_views(baseline, current):
            sigma = max(v.baseline_stddev, 1e-9)
            drop = (v.baseline_mean - v.current_mean) / sigma
            if drop >= self._sigma:
                out.append(RegressionRecord(
                    metric=v.metric, problem_id=baseline.problem_id,
                    baseline_mean=v.baseline_mean,
                    baseline_stddev=v.baseline_stddev,
                    current_mean=v.current_mean,
                    current_stddev=v.current_stddev,
                    sigma_drop=drop, timestamp=self._timestamp,
                ))
        return tuple(out)
