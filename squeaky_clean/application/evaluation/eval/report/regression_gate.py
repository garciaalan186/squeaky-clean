"""RegressionGate: judge sweep results against routing-stamped goldens (R5.2)."""

from __future__ import annotations

from datetime import datetime, timezone

from squeaky_clean.application.evaluation.eval.report.golden_baseline import (
    to_replicate_summary,
)
from squeaky_clean.application.evaluation.eval.report.regression_assessment import (
    RegressionAssessment,
)
from squeaky_clean.application.evaluation.eval.report.regression_detector import (
    RegressionDetector,
)
from squeaky_clean.application.evaluation.eval.report.regression_record import (
    RegressionRecord,
)
from squeaky_clean.application.evaluation.eval.run.eval_report_bundle import (
    EvalReportBundle,
)
from squeaky_clean.application.evaluation.eval.sweep.replicate_aggregator import (
    ReplicateAggregator,
)
from squeaky_clean.application.evaluation.eval.sweep.sweep_result import SweepResult


class RegressionGate:
    """Compares each sweep bundle against its problem's golden baseline.

    Verdicts: ``no golden`` (uncalibrated — never gates), ``not comparable``
    (model routing changed since calibration — a model delta, not a framework
    regression), ``OK``, or ``REGRESSION`` (>= 2 sigma drop, R5.2).
    """

    def __init__(self) -> None:
        self._detector: RegressionDetector = RegressionDetector()
        self._aggregator: ReplicateAggregator = ReplicateAggregator()

    def assess(
        self, result: SweepResult, models: dict[str, str],
    ) -> RegressionAssessment:
        """Return verdicts + regression records for every bundle in ``result``."""
        stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
        verdicts: list[str] = []
        records: list[RegressionRecord] = []
        for bundle in result.bundles:
            verdict, recs = self._one(bundle, models, stamp)
            verdicts.append(verdict)
            records.extend(recs)
        return RegressionAssessment(
            verdicts=tuple(verdicts), records=tuple(records),
        )

    def _one(
        self, bundle: EvalReportBundle, models: dict[str, str], stamp: str,
    ) -> tuple[str, tuple[RegressionRecord, ...]]:
        pid = bundle.problem.id
        golden = bundle.problem.golden_metrics
        if golden is None:
            return f"{pid}: no golden (uncalibrated)", ()
        if not golden.routing_matches(models):
            return f"{pid}: not comparable (routing changed since calibration)", ()
        current = self._aggregator.aggregate(pid, [bundle.metrics])
        baseline = to_replicate_summary(pid, golden)
        recs = tuple(self._detector.detect(baseline, current, stamp))
        if not recs:
            return (f"{pid}: OK (tests {bundle.metrics.tests_pass:.2f} vs golden "
                    f"{golden.tests_pass_mean:.2f}±{golden.tests_pass_stddev:.2f})"), ()
        worst = max(recs, key=lambda r: r.sigma_drop)
        return (f"{pid}: REGRESSION {worst.metric} {worst.current_mean:.2f} vs "
                f"{worst.baseline_mean:.2f}±{worst.baseline_stddev:.2f} "
                f"(drop {worst.sigma_drop:.1f}σ)"), recs
