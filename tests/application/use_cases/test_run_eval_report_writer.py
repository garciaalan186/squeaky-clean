"""Tests for RunEvalReportWriter: eval_report.json serialisation."""

import json
from pathlib import Path

from squeaky_clean.application.evaluation.eval.metrics.model.cost_breakdown import CostBreakdown
from squeaky_clean.application.evaluation.eval.metrics.model.eval_metrics import EvalMetrics
from squeaky_clean.application.evaluation.eval.metrics.model.test_outcome import TestOutcome
from squeaky_clean.application.evaluation.eval.run.eval_report_bundle import EvalReportBundle
from squeaky_clean.application.evaluation.eval.run.run_eval_report_writer import (
    RunEvalReportWriter,
)
from squeaky_clean.application.generation.validation.validation_report import ValidationReport
from squeaky_clean.application.shared.problem.problem_spec import ProblemSpec
from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.domain.value_objects.test_run_result import TestRunResult
from squeaky_clean.domain.value_objects.violation import Violation


def _bundle() -> EvalReportBundle:
    metrics = EvalMetrics(
        test_outcome=TestOutcome(tests_pass=0.5),
        cost=CostBreakdown(estimated_cost_usd=0.42),
    )
    problem = ProblemSpec(
        id="P0", slug="calculator", description="four-op calculator", tier=0,
        target_language=TargetLanguage.PYTHON,
        required_bounded_contexts=[], acceptance_criteria=["Given a calculator"],
        expected_module_count=(1, 1), expected_class_count=(1, 1),
        required_patterns=[],
    )
    violation = Violation(rule_name="DependencyRule", file_path="src/x.py",
                          message="domain imports infrastructure")
    return EvalReportBundle(
        problem=problem, metrics=metrics,
        test_run_result=TestRunResult(passed=2, failed=1, errors=1,
                                      duration_ms=77, raw_output="out"),
        validation=ValidationReport(violations=(violation,), files_scanned=3),
    )


def test_write_serialises_bundle_to_json(tmp_path: Path) -> None:
    path = tmp_path / "eval_report.json"
    RunEvalReportWriter().write(path, _bundle())
    data = json.loads(path.read_text())
    assert data["problem_id"] == "P0"
    assert data["description"] == "four-op calculator"
    assert data["schema_version"] == 2
    assert data["metrics"]["test_outcome"]["tests_pass"] == 0.5
    assert data["metrics"]["cost"]["estimated_cost_usd"] == 0.42
    assert data["tests"] == {"passed": 2, "failed": 1, "errors": 1,
                             "duration_ms": 77}
    assert data["violations"] == [{
        "rule_name": "DependencyRule", "file_path": "src/x.py",
        "message": "domain imports infrastructure",
    }]
    assert data["files_scanned"] == 3
    assert data["acceptance_criteria"] == ["Given a calculator"]


def test_write_creates_missing_parent_dirs_atomically(tmp_path: Path) -> None:
    """Nested target dirs are created and no temp file is left behind."""
    path = tmp_path / "run" / "problem-set-0-calculator-code" / "eval_report.json"
    RunEvalReportWriter().write(path, _bundle())
    assert path.is_file()
    assert [p.name for p in path.parent.iterdir()] == ["eval_report.json"]
