"""Tests for SweepProblemTable (extracted from SweepSummaryWriter)."""

from pathlib import Path

from squeaky_clean.application.evaluation.eval.metrics.model.cost_breakdown import CostBreakdown
from squeaky_clean.application.evaluation.eval.metrics.model.eval_metrics import EvalMetrics
from squeaky_clean.application.evaluation.eval.metrics.model.reliability_stats import (
    ReliabilityStats,
)
from squeaky_clean.application.evaluation.eval.metrics.model.test_outcome import TestOutcome
from squeaky_clean.application.evaluation.eval.run.eval_report_bundle import EvalReportBundle
from squeaky_clean.application.evaluation.eval.sweep.sweep_problem_table import (
    SweepProblemTable,
)
from squeaky_clean.application.evaluation.eval.sweep.sweep_result import SweepResult
from squeaky_clean.application.generation.validation.validation_report import ValidationReport
from squeaky_clean.application.shared.problem.problem_spec import ProblemSpec
from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.domain.value_objects.test_run_result import TestRunResult


def _bundle(pid: str, violations: int, error: str | None) -> EvalReportBundle:
    metrics = EvalMetrics(
        test_outcome=TestOutcome(tests_pass=1.0, functional_tests_pass=1.0),
        cost=CostBreakdown(estimated_cost_usd=0.1),
        reliability=ReliabilityStats(classes_fixed=0),
        architecture_violations=violations,
    )
    problem = ProblemSpec(
        id=pid, slug=pid.lower(), description="x", tier=0,
        target_language=TargetLanguage.PYTHON,
        required_bounded_contexts=[], acceptance_criteria=[],
        expected_module_count=(1, 1), expected_class_count=(1, 1),
        required_patterns=[],
    )
    return EvalReportBundle(
        problem=problem, metrics=metrics,
        test_run_result=TestRunResult(
            passed=1, failed=0, errors=0, duration_ms=10, raw_output="ok",
        ),
        validation=ValidationReport(violations=(), files_scanned=1),
        error=error,
    )


def _render(bundles: tuple[EvalReportBundle, ...]) -> str:
    result = SweepResult(
        run_dir=Path("/tmp/meta-evaluation_001_x"), bundles=bundles,
        total_cost_usd=0.1, total_duration_ms=10,
    )
    return "\n".join(SweepProblemTable().render(result))


def test_table_has_title_row_per_problem_and_caveats() -> None:
    text = _render((_bundle("P0", 0, None),))
    assert text.startswith("# Meta-Evaluation Sweep — meta-evaluation_001_x")
    assert "| P0 | 1.00" in text
    assert "n/a = not measured" in text
    assert "single sample per problem (N=1)" in text


def test_error_bundle_is_tagged_and_violations_flagged() -> None:
    text = _render((_bundle("P1", 2, "boom"),))
    assert "| P1 ⚠️ |" in text
    assert "| 2 ⚠ |" in text
