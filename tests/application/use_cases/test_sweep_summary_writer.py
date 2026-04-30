"""Tests for SweepSummaryWriter."""

from pathlib import Path

from squeaky_clean.application.dtos.eval_metrics import EvalMetrics
from squeaky_clean.application.dtos.eval_report_bundle import EvalReportBundle
from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.application.dtos.sweep_result import SweepResult
from squeaky_clean.application.dtos.test_run_result import TestRunResult
from squeaky_clean.application.dtos.validation_report import ValidationReport
from squeaky_clean.application.use_cases.sweep_summary_writer import SweepSummaryWriter
from squeaky_clean.domain.value_objects.target_language import TargetLanguage


def _bundle(pid: str, pass_rate: float, cost: float, fixed: int) -> EvalReportBundle:
    metrics = EvalMetrics.empty()
    metrics.tests_pass = pass_rate
    metrics.functional_tests_pass = pass_rate
    metrics.estimated_cost_usd = cost
    metrics.classes_fixed = fixed
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
    )


def test_write_renders_summary_table_and_totals(tmp_path: Path) -> None:
    bundles = (_bundle("P0", 1.0, 0.10, 0), _bundle("P1", 0.5, 0.20, 1))
    result = SweepResult(
        run_dir=tmp_path, bundles=bundles,
        total_cost_usd=0.30, total_duration_ms=5000,
    )
    SweepSummaryWriter().write(result)
    text = (tmp_path / "SUMMARY.md").read_text()
    assert "| P0 | 1.00" in text
    assert "| P1 | 0.50" in text
    assert "problems at 100% (overall): 1/2" in text
    assert "classes fixed by Sonnet fixer: 1" in text
    assert (tmp_path / "metrics.json").is_file()
