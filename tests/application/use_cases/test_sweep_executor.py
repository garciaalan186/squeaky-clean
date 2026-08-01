"""Tests for SweepExecutor: sweep POLICY without any interface/ imports (R6.7)."""

from pathlib import Path

from squeaky_clean.application.evaluation.eval.run.eval_report_bundle import EvalReportBundle
from squeaky_clean.application.evaluation.eval.sweep.sweep_executor import SweepExecutor
from squeaky_clean.application.evaluation.eval.sweep.sweep_executor_deps import SweepExecutorDeps
from squeaky_clean.application.evaluation.eval.sweep.sweep_request import SweepRequest
from squeaky_clean.application.generation.validation.validation_report import ValidationReport
from squeaky_clean.application.shared.problem.problem_spec import ProblemSpec
from squeaky_clean.domain.entities.eval_metrics import EvalMetrics
from squeaky_clean.domain.interfaces.run_logger import RunLogger
from squeaky_clean.domain.value_objects.metrics.cost_breakdown import CostBreakdown
from squeaky_clean.domain.value_objects.metrics.test_outcome import TestOutcome
from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.domain.value_objects.test_run_result import TestRunResult


class _RecordingLogger(RunLogger):
    def __init__(self) -> None:
        self.events: list[str] = []

    def event(self, kind: str, **fields: object) -> None:
        self.events.append(kind)


def _problem(pid: str, tier: int) -> ProblemSpec:
    return ProblemSpec(
        id=pid, slug=f"slug{tier}", description="x", tier=tier,
        target_language=TargetLanguage.PYTHON,
        required_bounded_contexts=[], acceptance_criteria=[],
        expected_module_count=(1, 1), expected_class_count=(1, 1),
        required_patterns=[],
    )


def _bundle(pid: str, cost: float) -> EvalReportBundle:
    metrics = EvalMetrics(
        test_outcome=TestOutcome(tests_pass=1.0),
        cost=CostBreakdown(estimated_cost_usd=cost),
    )
    return EvalReportBundle(
        problem=_problem(pid, 0), metrics=metrics,
        test_run_result=TestRunResult(
            passed=1, failed=0, errors=0, duration_ms=10, raw_output="ok",
        ),
        validation=ValidationReport(violations=(), files_scanned=1),
    )


def _runner(problem: ProblemSpec, run_dir: Path) -> EvalReportBundle:
    return _bundle(problem.id, cost=0.5)


def _no_models() -> dict[str, str]:
    return {}


def test_execute_aggregates_and_writes_summary(tmp_path: Path) -> None:
    root = tmp_path / "results"
    root.mkdir()
    logger = _RecordingLogger()
    executor = SweepExecutor(SweepExecutorDeps(
        run_root=root, runner=_runner, models=_no_models, logger=logger,
        replay_miss_error=RuntimeError,
    ))
    result = executor.execute(SweepRequest(
        problems=(_problem("P0", 0), _problem("P1", 1)), max_parallel=2,
    ))
    assert result.total_cost_usd == 1.0
    assert [b.problem.id for b in result.bundles] == ["P0", "P1"]
    assert (result.run_dir / "SUMMARY.md").is_file()
    assert (result.run_dir / "metrics.json").is_file()
    assert result.run_dir.parent == root
    assert logger.events[0] == "sweep_started"
    assert logger.events[-1] == "sweep_complete"
    # R5.2: one regression-gate verdict per bundle (no goldens -> uncalibrated).
    assert len(result.regression_verdicts) == 2
