"""EvalReportBundle DTO: values needed to serialise a per-problem eval report."""

from dataclasses import dataclass

from squeaky_clean.application.dtos.eval_metrics import EvalMetrics
from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.application.dtos.test_run_result import TestRunResult
from squeaky_clean.application.dtos.validation_report import ValidationReport


@dataclass(frozen=True)
class EvalReportBundle:
    """Immutable bundle of everything needed to write one eval_report.json.

    Collecting these five objects on one DTO lets RunEval's report
    writer take a single argument (respecting the <=2-args rule) while
    still having access to the ProblemSpec, the computed metrics, the
    test outcome, and the architecture validation report.
    """

    problem: ProblemSpec
    metrics: EvalMetrics
    test_run_result: TestRunResult
    validation: ValidationReport
    error: str | None = None
