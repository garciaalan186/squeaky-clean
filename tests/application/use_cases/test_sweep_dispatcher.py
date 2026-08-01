"""Tests for SweepDispatcher: per-problem error POLICY (R6.7)."""

from collections.abc import Callable
from pathlib import Path

import pytest

from squeaky_clean.application.evaluation.eval.metrics.model.cost_breakdown import CostBreakdown
from squeaky_clean.application.evaluation.eval.metrics.model.eval_metrics import EvalMetrics
from squeaky_clean.application.evaluation.eval.metrics.model.test_outcome import TestOutcome
from squeaky_clean.application.evaluation.eval.run.eval_report_bundle import EvalReportBundle
from squeaky_clean.application.evaluation.eval.sweep.sweep_dispatcher import SweepDispatcher
from squeaky_clean.application.evaluation.eval.sweep.sweep_executor_deps import SweepExecutorDeps
from squeaky_clean.application.evaluation.eval.sweep.sweep_request import SweepRequest
from squeaky_clean.application.generation.validation.validation_report import ValidationReport
from squeaky_clean.application.shared.gateways.cost_gate import BudgetExceededError
from squeaky_clean.application.shared.problem.problem_spec import ProblemSpec
from squeaky_clean.domain.interfaces.run_logger import RunLogger
from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.domain.value_objects.test_run_result import TestRunResult


class _FakeReplayMiss(RuntimeError):
    pass


class _RecordingLogger(RunLogger):
    def __init__(self) -> None:
        self.events: list[tuple[str, dict[str, object]]] = []

    def event(self, kind: str, **fields: object) -> None:
        self.events.append((kind, dict(fields)))


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


def _no_models() -> dict[str, str]:
    return {}


def _dispatcher(
    runner: Callable[[ProblemSpec, Path], EvalReportBundle],
    logger: _RecordingLogger, tmp_path: Path,
) -> SweepDispatcher:
    return SweepDispatcher(SweepExecutorDeps(
        run_root=tmp_path,
        runner=runner,
        models=_no_models,
        logger=logger,
        replay_miss_error=_FakeReplayMiss,
    ))


def test_dispatch_preserves_request_order(tmp_path: Path) -> None:
    logger = _RecordingLogger()

    def runner(problem: ProblemSpec, run_dir: Path) -> EvalReportBundle:
        return _bundle(problem.id, cost=0.5)

    bundles = _dispatcher(runner, logger, tmp_path).dispatch(
        SweepRequest(problems=(_problem("P0", 0), _problem("P1", 1)),
                     max_parallel=2),
        tmp_path,
    )
    assert [b.problem.id for b in bundles] == ["P0", "P1"]
    kinds = [k for k, _ in logger.events]
    assert kinds.count("problem_started") == 2
    assert kinds.count("problem_complete") == 2


def test_generic_failure_becomes_failure_bundle(tmp_path: Path) -> None:
    logger = _RecordingLogger()

    def runner(problem: ProblemSpec, run_dir: Path) -> EvalReportBundle:
        raise ValueError("boom")

    bundles = _dispatcher(runner, logger, tmp_path).dispatch(
        SweepRequest(problems=(_problem("P0", 0),), max_parallel=1), tmp_path,
    )
    assert bundles[0].error is not None
    assert "boom" in bundles[0].error
    assert [k for k, _ in logger.events] == ["problem_started", "problem_failed"]


def test_budget_exceeded_reraises_with_event(tmp_path: Path) -> None:
    logger = _RecordingLogger()

    def runner(problem: ProblemSpec, run_dir: Path) -> EvalReportBundle:
        raise BudgetExceededError("cap reached")

    with pytest.raises(BudgetExceededError):
        _dispatcher(runner, logger, tmp_path).dispatch(
            SweepRequest(problems=(_problem("P0", 0),), max_parallel=1),
            tmp_path,
        )
    assert [k for k, _ in logger.events] == [
        "problem_started", "sweep_budget_exceeded",
    ]


def test_replay_cache_miss_reraises_with_event(tmp_path: Path) -> None:
    logger = _RecordingLogger()

    def runner(problem: ProblemSpec, run_dir: Path) -> EvalReportBundle:
        raise _FakeReplayMiss("prompt absent from cache")

    with pytest.raises(_FakeReplayMiss):
        _dispatcher(runner, logger, tmp_path).dispatch(
            SweepRequest(problems=(_problem("P0", 0),), max_parallel=1),
            tmp_path,
        )
    assert [k for k, _ in logger.events] == [
        "problem_started", "replay_cache_miss",
    ]
