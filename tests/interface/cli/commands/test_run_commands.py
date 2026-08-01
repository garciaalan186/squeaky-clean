"""Tests for RunCommands routing (no pipeline is run)."""

from pathlib import Path

import pytest

from squeaky_clean.application.shared.problem.problem_spec import ProblemSpec
from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.infrastructure.llm.model_router import ModelRouter
from squeaky_clean.interface.cli.commands.run_commands import RunCommands
from squeaky_clean.interface.cli.invocations.run_invocation import RunInvocation
from squeaky_clean.interface.cli.replicates.replicate_run_outcome import ReplicateRunOutcome
from squeaky_clean.interface.cli.replicates.replicate_runner import ReplicateRunner


def _problem(pid: str = "P0") -> ProblemSpec:
    return ProblemSpec(
        id=pid, tier=0, slug="calc", description="x",
        required_bounded_contexts=[], acceptance_criteria=[],
        expected_module_count=(1, 1), expected_class_count=(1, 1),
        required_patterns=[], target_language=TargetLanguage.PYTHON,
    )


def test_dispatch_routes_to_replicates_when_replicates_gt_1(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen: list[str] = []

    def fake_run(self: ReplicateRunner, problem: ProblemSpec) -> ReplicateRunOutcome:
        seen.append(problem.id)
        return ReplicateRunOutcome(summary_path=Path("s.json"), runs=2)

    monkeypatch.setattr(ReplicateRunner, "run", fake_run)
    run = RunInvocation(problem_ids=("P0",), replicates=2)
    assert RunCommands(ModelRouter()).dispatch(_problem(), run) == 0
    assert seen == ["P0"]


def test_single_resolves_the_problem_id(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: list[str] = []

    def fake_dispatch(self: RunCommands, problem: ProblemSpec, run: RunInvocation) -> int:
        seen.append(problem.id)
        return 0

    monkeypatch.setattr(RunCommands, "dispatch", fake_dispatch)
    run = RunInvocation(problem_ids=("P1",))
    assert RunCommands(ModelRouter()).single("P1", run) == 0
    assert seen == ["P1"]


def test_replicated_dispatches_every_problem_and_returns_max_code(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    codes = {"P0": 0, "P1": 1}
    seen: list[str] = []

    def fake_dispatch(self: RunCommands, problem: ProblemSpec, run: RunInvocation) -> int:
        seen.append(problem.id)
        return codes[problem.id]

    monkeypatch.setattr(RunCommands, "dispatch", fake_dispatch)
    run = RunInvocation(problem_ids=("P0", "P1"), replicates=2)
    assert RunCommands(ModelRouter()).replicated(run) == 1
    assert seen == ["P0", "P1"]
