"""EvalReportBundle DTO: values needed to serialise a per-problem eval report."""

from dataclasses import dataclass

from squeaky_clean.application.evaluation.eval.metrics.model.eval_metrics import EvalMetrics
from squeaky_clean.application.generation.validation.validation_report import ValidationReport
from squeaky_clean.application.shared.problem.problem_spec import ProblemSpec
from squeaky_clean.domain.value_objects.test_run_result import TestRunResult


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
