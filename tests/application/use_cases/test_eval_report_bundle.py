"""Tests for the EvalReportBundle DTO."""

import dataclasses

import pytest

from squeaky_clean.application.evaluation.eval.metrics.model.eval_metrics import EvalMetrics
from squeaky_clean.application.evaluation.eval.run.eval_report_bundle import EvalReportBundle
from squeaky_clean.application.generation.validation.validation_report import ValidationReport
from squeaky_clean.application.shared.problem.problem_spec import ProblemSpec
from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.domain.value_objects.test_run_result import TestRunResult


def _bundle(error: str | None = None) -> EvalReportBundle:
    problem = ProblemSpec(
        id="P0", slug="calculator", description="x", tier=0,
        target_language=TargetLanguage.PYTHON,
        required_bounded_contexts=[], acceptance_criteria=[],
        expected_module_count=(1, 1), expected_class_count=(1, 1),
        required_patterns=[],
    )
    return EvalReportBundle(
        problem=problem, metrics=EvalMetrics.empty(),
        test_run_result=TestRunResult(passed=1, failed=0, errors=0,
                                      duration_ms=10, raw_output="ok"),
        validation=ValidationReport(violations=(), files_scanned=1),
        error=error,
    )


def test_error_defaults_to_none() -> None:
    bundle = _bundle()
    assert bundle.error is None


def test_stores_error_and_components() -> None:
    bundle = _bundle(error="boom")
    assert bundle.error == "boom"
    assert bundle.problem.id == "P0"
    assert bundle.test_run_result.passed == 1
    assert bundle.validation.is_valid


def test_is_frozen() -> None:
    bundle = _bundle()
    with pytest.raises(dataclasses.FrozenInstanceError):
        bundle.error = "later"  # type: ignore[misc]
