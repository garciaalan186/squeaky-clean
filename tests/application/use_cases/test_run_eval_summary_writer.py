"""Tests for RunEvalSummaryWriter: SUMMARY.md rendering branches."""

from pathlib import Path

from squeaky_clean.application.evaluation.eval.run.eval_report_bundle import EvalReportBundle
from squeaky_clean.application.evaluation.eval.run.run_eval_summary_writer import (
    RunEvalSummaryWriter,
)
from squeaky_clean.application.generation.validation.validation_report import ValidationReport
from squeaky_clean.application.shared.problem.problem_spec import ProblemSpec
from squeaky_clean.domain.entities.eval_metrics import EvalMetrics
from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.domain.value_objects.test_run_result import TestRunResult
from squeaky_clean.domain.value_objects.violation import Violation


def _bundle(
    status: str, tr: TestRunResult, validation: ValidationReport,
) -> EvalReportBundle:
    metrics = EvalMetrics.empty()
    metrics.tests_pass = 0.75
    metrics.test_status = status
    metrics.estimated_cost_usd = 0.1234
    metrics.total_wall_clock_ms = 4200
    problem = ProblemSpec(
        id="P0", slug="calculator", description="x", tier=0,
        target_language=TargetLanguage.PYTHON,
        required_bounded_contexts=[], acceptance_criteria=[],
        expected_module_count=(1, 1), expected_class_count=(1, 1),
        required_patterns=[],
    )
    return EvalReportBundle(problem=problem, metrics=metrics,
                            test_run_result=tr, validation=validation)


def _ok_tr() -> TestRunResult:
    return TestRunResult(passed=3, failed=0, errors=0, duration_ms=10,
                         raw_output="ok")


def test_write_renders_pass_rate_row_legend_and_routing(tmp_path: Path) -> None:
    bundle = _bundle("ok", _ok_tr(), ValidationReport(violations=(), files_scanned=2))
    path = tmp_path / "SUMMARY.md"
    RunEvalSummaryWriter().write(path, bundle, models={
        "architect": "claude-opus-4-8", "icp": "claude-haiku-4-5",
    })
    text = path.read_text()
    assert "| P0 | 0.75 | 0 | 0.1234 | 4200 |" in text
    assert "single sample (N=1)" in text
    assert "pass rate = functional acceptance criteria only" in text
    assert "ARCHITECT" in text and "-> claude-opus-4-8" in text
    assert "ICP" in text and "-> claude-haiku-4-5" in text
    assert "- test status: ok" in text


def test_write_build_failed_renders_dash_not_zero(tmp_path: Path) -> None:
    """A build failure must not masquerade as a measured 0.00 pass rate."""
    tr = TestRunResult(passed=0, failed=0, errors=3, duration_ms=10,
                       raw_output="E   ImportError: boom")
    bundle = _bundle("build_failed", tr,
                     ValidationReport(violations=(), files_scanned=2))
    path = tmp_path / "SUMMARY.md"
    RunEvalSummaryWriter().write(path, bundle)
    text = path.read_text()
    assert "— (build_failed)" in text
    assert "| P0 | 0.75" not in text
    # errors > 0 → the failure excerpt section appears with the raw output
    assert "## Test Failure Excerpt" in text
    assert "E   ImportError: boom" in text


def test_write_without_models_leaves_routing_section_empty(tmp_path: Path) -> None:
    bundle = _bundle("ok", _ok_tr(), ValidationReport(violations=(), files_scanned=2))
    path = tmp_path / "SUMMARY.md"
    RunEvalSummaryWriter().write(path, bundle)
    text = path.read_text()
    assert "## Model Routing" in text
    assert " -> " not in text


def test_write_lists_architectural_violations(tmp_path: Path) -> None:
    violation = Violation(rule_name="GranularityRule", file_path="src/big.py",
                          message="file exceeds 80 lines")
    bundle = _bundle("ok", _ok_tr(),
                     ValidationReport(violations=(violation,), files_scanned=5))
    path = tmp_path / "SUMMARY.md"
    RunEvalSummaryWriter().write(path, bundle)
    text = path.read_text()
    assert "## Architectural Violations" in text
    assert "- [GranularityRule] src/big.py: file exceeds 80 lines" in text
    assert "- architecture violations: 1" in text
