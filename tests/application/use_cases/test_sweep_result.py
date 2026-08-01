"""Tests for the SweepResult DTO."""

import dataclasses
from pathlib import Path

import pytest

from squeaky_clean.application.evaluation.eval.metrics.model.eval_metrics import EvalMetrics
from squeaky_clean.application.evaluation.eval.run.eval_report_bundle import EvalReportBundle
from squeaky_clean.application.evaluation.eval.sweep.sweep_result import SweepResult
from squeaky_clean.application.generation.validation.validation_report import ValidationReport
from squeaky_clean.application.shared.problem.problem_spec import ProblemSpec
from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.domain.value_objects.test_run_result import TestRunResult


def _bundle() -> EvalReportBundle:
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
    )


def test_regression_verdicts_default_to_empty_tuple() -> None:
    result = SweepResult(run_dir=Path("/tmp/run"), bundles=(_bundle(),),
                         total_cost_usd=0.1, total_duration_ms=100)
    assert result.regression_verdicts == ()


def test_stores_run_dir_bundles_and_verdicts() -> None:
    bundles = (_bundle(), _bundle())
    result = SweepResult(
        run_dir=Path("/tmp/run"), bundles=bundles, total_cost_usd=0.2,
        total_duration_ms=200, regression_verdicts=("PASS", "REGRESSED"),
    )
    assert result.run_dir == Path("/tmp/run")
    assert result.bundles == bundles
    assert result.total_cost_usd == 0.2
    assert result.regression_verdicts == ("PASS", "REGRESSED")


def test_is_frozen() -> None:
    result = SweepResult(run_dir=Path("/x"), bundles=(),
                         total_cost_usd=0.0, total_duration_ms=0)
    with pytest.raises(dataclasses.FrozenInstanceError):
        result.total_cost_usd = 1.0  # type: ignore[misc]
