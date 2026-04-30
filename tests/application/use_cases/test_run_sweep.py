"""Tests for RunSweep."""

from pathlib import Path
from typing import cast
from unittest.mock import Mock

import pytest

from squeaky_clean.application.dtos.eval_metrics import EvalMetrics
from squeaky_clean.application.dtos.eval_report_bundle import EvalReportBundle
from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.application.dtos.sweep_request import SweepRequest
from squeaky_clean.application.dtos.test_run_result import TestRunResult
from squeaky_clean.application.dtos.validation_report import ValidationReport
from squeaky_clean.application.use_cases.run_sweep import RunSweep
from squeaky_clean.application.use_cases.run_sweep_deps import RunSweepDeps
from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.infrastructure.llm.model_router import ModelRouter
from squeaky_clean.interface.cli.dependency_builder import DependencyBuilder


def _problem(pid: str, tier: int) -> ProblemSpec:
    return ProblemSpec(
        id=pid, slug=f"slug{tier}", description="x", tier=tier,
        target_language=TargetLanguage.PYTHON,
        required_bounded_contexts=[], acceptance_criteria=[],
        expected_module_count=(1, 1), expected_class_count=(1, 1),
        required_patterns=[],
    )


def _bundle(pid: str, cost: float) -> EvalReportBundle:
    metrics = EvalMetrics.empty()
    metrics.tests_pass = 1.0
    metrics.estimated_cost_usd = cost
    return EvalReportBundle(
        problem=_problem(pid, 0), metrics=metrics,
        test_run_result=TestRunResult(
            passed=1, failed=0, errors=0, duration_ms=10, raw_output="ok",
        ),
        validation=ValidationReport(violations=(), files_scanned=1),
    )


@pytest.fixture
def tmp_run_root(tmp_path: Path) -> Path:
    root = tmp_path / "results"
    root.mkdir()
    return root


def test_execute_runs_problems_in_parallel(tmp_run_root: Path) -> None:
    builder = Mock(spec=DependencyBuilder)
    builder.build.return_value = Mock()
    deps = RunSweepDeps(
        dependency_builder=cast(DependencyBuilder, builder),
        router=ModelRouter(), run_root=tmp_run_root,
    )
    sweep = RunSweep(deps)

    captured: list[str] = []

    def fake_execute_in(self: object, problem: ProblemSpec, run_dir: Path) -> EvalReportBundle:  # noqa: ARG001
        captured.append(problem.id)
        return _bundle(problem.id, cost=0.5)

    from squeaky_clean.application.use_cases import run_eval as run_eval_module

    monkey = run_eval_module.RunEval.execute_in
    run_eval_module.RunEval.execute_in = fake_execute_in  # type: ignore[method-assign]
    try:
        result = sweep.execute(SweepRequest(
            problems=(_problem("P0", 0), _problem("P1", 1)), max_parallel=2,
        ))
    finally:
        run_eval_module.RunEval.execute_in = monkey  # type: ignore[method-assign]

    assert sorted(captured) == ["P0", "P1"]
    assert result.total_cost_usd == 1.0
    assert (result.run_dir / "SUMMARY.md").is_file()
    assert (result.run_dir / "metrics.json").is_file()
