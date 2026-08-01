"""Routing tests for SqueakyCleanCLI.run over CLIRequest — stubs only, no API calls."""

from __future__ import annotations

import pytest

from squeaky_clean.infrastructure.llm.model_router import ModelRouter
from squeaky_clean.interface.cli.cli_args_parser import CLIArgsParser
from squeaky_clean.interface.cli.invocations.cli_invocation_mapper import CLIInvocationMapper
from squeaky_clean.interface.cli.invocations.cli_request import CLIRequest
from squeaky_clean.interface.cli.invocations.maintenance_invocation import MaintenanceInvocation
from squeaky_clean.interface.cli.invocations.micro_eval_invocation import MicroEvalInvocation
from squeaky_clean.interface.cli.invocations.recovery_invocation import RecoveryInvocation
from squeaky_clean.interface.cli.invocations.run_invocation import RunInvocation
from squeaky_clean.interface.cli.micro_eval_command import MicroEvalCommand
from squeaky_clean.interface.cli.squeaky_clean_cli import SqueakyCleanCLI

_Seen = dict[str, tuple[object, ...]]


def _request(argv: list[str]) -> CLIRequest:
    return CLIInvocationMapper().map(CLIArgsParser().parse(argv))


def _stub_branch(
    monkeypatch: pytest.MonkeyPatch, name: str, seen: _Seen,
) -> None:
    def fake(self: SqueakyCleanCLI, *branch_args: object) -> int:
        seen[name] = branch_args
        return 0

    monkeypatch.setattr(SqueakyCleanCLI, name, fake)


def _run_invocation(seen: _Seen, name: str, index: int) -> RunInvocation:
    value = seen[name][index]
    assert isinstance(value, RunInvocation)
    return value


def test_problem_p2_replicates_3_routes_to_replicated(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen: _Seen = {}
    _stub_branch(monkeypatch, "_replicated", seen)
    assert SqueakyCleanCLI().run(_request(["--problem", "P2", "--replicates", "3"])) == 0
    assert isinstance(seen["_replicated"][0], ModelRouter)
    run = _run_invocation(seen, "_replicated", 1)
    assert run.problem_ids == ("P2",)
    assert run.replicates == 3


def test_single_problem_routes_to_single(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: _Seen = {}
    _stub_branch(monkeypatch, "_single", seen)
    _stub_branch(monkeypatch, "_sweep", seen)
    argv = ["--problem", "P0", "--max-parallel", "1"]
    assert SqueakyCleanCLI().run(_request(argv)) == 0
    assert seen["_single"][1] == "P0"
    assert isinstance(seen["_single"][2], RunInvocation)
    assert "_sweep" not in seen


def test_single_problem_default_parallelism_routes_to_sweep(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # `--problem P0` alone keeps the pre-R6.5 route: default --max-parallel
    # is 4, so the single-problem run still goes through the sweep path.
    seen: _Seen = {}
    _stub_branch(monkeypatch, "_sweep", seen)
    assert SqueakyCleanCLI().run(_request(["--problem", "P0"])) == 0
    assert _run_invocation(seen, "_sweep", 1).problem_ids == ("P0",)


def test_multi_problem_routes_to_sweep(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: _Seen = {}
    _stub_branch(monkeypatch, "_sweep", seen)
    assert SqueakyCleanCLI().run(_request(["--problems", "P0,P1"])) == 0
    assert _run_invocation(seen, "_sweep", 1).problem_ids == ("P0", "P1")


def test_micro_evals_routes_to_micro_eval_command(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen: _Seen = {}

    def fake_run(self: MicroEvalCommand, invocation: MicroEvalInvocation) -> int:
        seen["invocation"] = (invocation,)
        return 0

    monkeypatch.setattr(MicroEvalCommand, "run", fake_run)
    assert SqueakyCleanCLI().run(_request(["--micro-evals"])) == 0
    invocation = seen["invocation"][0]
    assert isinstance(invocation, MicroEvalInvocation)
    assert invocation.enabled is True


def test_rebuild_dashboard_routes_to_dashboard(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen: _Seen = {}
    _stub_branch(monkeypatch, "_rebuild_dashboard", seen)
    assert SqueakyCleanCLI().run(_request(["--rebuild-dashboard"])) == 0
    assert "_rebuild_dashboard" in seen


def test_resume_routes_to_resume_with_maintenance_slice(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen: _Seen = {}
    _stub_branch(monkeypatch, "_resume", seen)
    assert SqueakyCleanCLI().run(_request(["--resume", "rundir", "--problem", "P1"])) == 0
    maint = seen["_resume"][1]
    assert isinstance(maint, MaintenanceInvocation)
    assert maint.resume_run_dir == "rundir"


def _recovery(seen: _Seen, name: str, index: int) -> RecoveryInvocation:
    value = seen[name][index]
    assert isinstance(value, RecoveryInvocation)
    return value


def test_recovery_family_routes_on_recovery_slice(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    seen: _Seen = {}
    for name in ("_triage", "_refactor_emit", "_recover_emit", "_recover"):
        _stub_branch(monkeypatch, name, seen)
    assert SqueakyCleanCLI().run(_request(["--triage", "v.json"])) == 0
    assert SqueakyCleanCLI().run(_request(["--refactor", "r.squib"])) == 0
    assert SqueakyCleanCLI().run(_request(["--recover-from", "proj"])) == 0
    assert SqueakyCleanCLI().run(_request(["--squib-file", "s.squib"])) == 0
    assert _recovery(seen, "_triage", 0).triage == "v.json"
    assert _recovery(seen, "_refactor_emit", 0).refactor == "r.squib"
    assert _recovery(seen, "_recover_emit", 0).recover_from == "proj"
    assert _recovery(seen, "_recover", 1).squib_file == "s.squib"
