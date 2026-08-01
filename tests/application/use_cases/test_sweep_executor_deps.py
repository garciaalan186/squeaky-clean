"""Tests for SweepExecutorDeps."""

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from squeaky_clean.application.evaluation.eval.run.eval_report_bundle import EvalReportBundle
from squeaky_clean.application.evaluation.eval.sweep.sweep_executor_deps import SweepExecutorDeps
from squeaky_clean.application.shared.problem.problem_spec import ProblemSpec
from squeaky_clean.domain.interfaces.run_logger import NullRunLogger


def _runner(problem: ProblemSpec, run_dir: Path) -> EvalReportBundle:
    raise NotImplementedError


def _deps(tmp_path: Path) -> SweepExecutorDeps:
    return SweepExecutorDeps(
        run_root=tmp_path,
        runner=_runner,
        models=lambda: {"icp": "claude-haiku"},
        logger=NullRunLogger(),
        replay_miss_error=RuntimeError,
    )


def test_holds_injected_collaborators(tmp_path: Path) -> None:
    deps = _deps(tmp_path)
    assert deps.run_root == tmp_path
    assert deps.models() == {"icp": "claude-haiku"}
    assert deps.replay_miss_error is RuntimeError


def test_is_frozen(tmp_path: Path) -> None:
    deps = _deps(tmp_path)
    with pytest.raises(FrozenInstanceError):
        deps.run_root = tmp_path / "other"  # type: ignore[misc]
