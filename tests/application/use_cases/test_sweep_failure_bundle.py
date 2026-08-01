"""Tests for SweepFailureBundle crash-to-report conversion."""

from squeaky_clean.application.evaluation.eval.metrics.model.eval_metrics import EvalMetrics
from squeaky_clean.application.evaluation.eval.sweep.sweep_failure_bundle import SweepFailureBundle
from squeaky_clean.application.shared.problem.problem_spec import ProblemSpec
from squeaky_clean.domain.value_objects.target_language import TargetLanguage


def _problem() -> ProblemSpec:
    return ProblemSpec(
        id="P0", slug="calculator", description="x", tier=0,
        target_language=TargetLanguage.PYTHON,
        required_bounded_contexts=[], acceptance_criteria=[],
        expected_module_count=(1, 1), expected_class_count=(1, 1),
        required_patterns=[],
    )


def test_build_wraps_error_in_zero_metric_bundle() -> None:
    error = "Traceback (most recent call last):\nValueError: boom"
    bundle = SweepFailureBundle().build(_problem(), error)
    assert bundle.problem.id == "P0"
    assert bundle.metrics == EvalMetrics.empty()
    assert bundle.test_run_result.passed == 0
    assert bundle.test_run_result.errors == 1
    assert bundle.test_run_result.raw_output == error
    assert bundle.validation.files_scanned == 0
    assert bundle.error == "ValueError: boom"


def test_build_excerpts_only_last_2000_chars_of_long_error() -> None:
    error = "x" * 3000 + "\nRuntimeError: tail"
    bundle = SweepFailureBundle().build(_problem(), error)
    assert len(bundle.test_run_result.raw_output) == 2000
    assert bundle.test_run_result.raw_output.endswith("RuntimeError: tail")
    assert bundle.error == "RuntimeError: tail"


def test_build_empty_error_reports_unknown() -> None:
    bundle = SweepFailureBundle().build(_problem(), "")
    assert bundle.error == "unknown"
    assert bundle.test_run_result.raw_output == ""
