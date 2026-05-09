"""SweepFailureBundle: builds an EvalReportBundle for a problem that crashed."""

from squeaky_clean.application.dtos.eval_metrics import EvalMetrics
from squeaky_clean.application.dtos.eval_report_bundle import EvalReportBundle
from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.application.dtos.test_run_result import TestRunResult
from squeaky_clean.application.dtos.validation_report import ValidationReport

_EXCERPT_CHARS: int = 2000


class SweepFailureBundle:
    """Wraps a sweep-time exception in an EvalReportBundle for the summary."""

    def build(self, problem: ProblemSpec, error: str) -> EvalReportBundle:
        """Return a zero-metric bundle with ``error`` recorded for the report."""
        return EvalReportBundle(
            problem=problem, metrics=EvalMetrics.empty(),
            test_run_result=TestRunResult(
                passed=0, failed=0, errors=1, duration_ms=0,
                raw_output=error[-_EXCERPT_CHARS:],
            ),
            validation=ValidationReport(violations=(), files_scanned=0),
            error=error.splitlines()[-1] if error else "unknown",
        )
