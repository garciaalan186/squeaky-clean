"""Tests for CLIInvocationMapper: flag namespace -> per-command invocations (R6.5)."""

from squeaky_clean.interface.cli.cli_args_parser import CLIArgsParser
from squeaky_clean.interface.cli.invocations.cli_invocation_mapper import CLIInvocationMapper
from squeaky_clean.interface.cli.invocations.cli_request import CLIRequest


def _map(argv: list[str]) -> CLIRequest:
    return CLIInvocationMapper().map(CLIArgsParser().parse(argv))


def test_run_flags_land_in_run_invocation() -> None:
    req = _map(["--problem", "P2", "--replicates", "3", "--seed", "5",
                "--max-parallel", "2", "--model-override", "m1"])
    assert req.run.problem_ids == ("P2",)
    assert req.run.replicates == 3
    assert req.run.max_parallel == 2
    assert req.run.model_override == "m1"
    assert req.run.settings.seed == 5


def test_run_settings_carry_retry_budget_cache_and_infra() -> None:
    req = _map(["--problem", "P0", "--max-icp-retries", "4",
                "--max-cost-usd", "2.5", "--no-prompt-cache",
                "--infra", "auto", "--replay-only", "--deterministic",
                "--architect-mode", "free"])
    s = req.run.settings
    assert s.retry.max_icp_retries == 4
    assert s.budget.max_cost_usd == 2.5
    assert s.cache.enabled is False
    assert s.infra.infrastructure_mode == "auto"
    assert s.replay_only is True
    assert s.deterministic is True
    assert s.architect_mode == "free"


def test_recovery_flags_land_in_recovery_invocation() -> None:
    req = _map(["--recover-from", "proj", "--recover-out", "o.squib",
                "--language", "java", "--criteria", "a, b"])
    assert req.recovery.recover_from == "proj"
    assert req.recovery.recover_out == "o.squib"
    assert req.recovery.recover_language == "java"
    assert req.recovery.criteria == ("a", "b")


def test_triage_refactor_and_squib_flags_land_in_recovery() -> None:
    req = _map(["--squib-file", "s.squib", "--legacy-tests", "t",
                "--triage", "v.json", "--refactor", "r.squib",
                "--plan", "p.json", "--refactor-out", "out.squib"])
    rec = req.recovery
    assert (rec.squib_file, rec.legacy_tests) == ("s.squib", "t")
    assert (rec.triage, rec.refactor) == ("v.json", "r.squib")
    assert (rec.plan, rec.refactor_out) == ("p.json", "out.squib")


def test_micro_eval_invocation_gets_flag_model_and_settings() -> None:
    req = _map(["--micro-evals", "--model-override", "m2", "--seed", "9"])
    assert req.micro_eval.enabled is True
    assert req.micro_eval.model_override == "m2"
    assert req.micro_eval.settings.seed == 9


def test_maintenance_invocation_gets_resume_and_problem_identity() -> None:
    req = _map(["--resume", "rundir", "--problem", "P1"])
    assert req.maintenance.resume_run_dir == "rundir"
    assert req.maintenance.rebuild_dashboard is False
    assert req.maintenance.problem_ids == ("P1",)


def test_one_settings_object_shared_by_all_invocations() -> None:
    req = _map(["--problem", "P0"])
    assert req.run.settings is req.recovery.settings
    assert req.run.settings is req.micro_eval.settings
    assert req.run.settings is req.maintenance.settings
