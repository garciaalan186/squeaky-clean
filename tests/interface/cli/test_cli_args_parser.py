"""Tests for CLIArgsParser."""

import pytest

from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.interface.cli.cli_args_parser import CLIArgsParser
from squeaky_clean.interface.cli.problem_resolver import ProblemResolver


def test_single_problem_via_problem_flag() -> None:
    args = CLIArgsParser().parse(["--problem", "P0"])
    assert args.problem_ids == ("P0",)
    assert args.max_parallel == 4


def test_problems_csv_list_parsed() -> None:
    args = CLIArgsParser().parse(["--problems", "P0,P1JS, P2TS"])
    assert args.problem_ids == ("P0", "P1JS", "P2TS")


def test_sweep_flag_yields_all_problems() -> None:
    args = CLIArgsParser().parse(["--sweep"])
    assert len(args.problem_ids) == 20
    assert "P0" in args.problem_ids
    assert "P0GO" in args.problem_ids
    assert "P0RUST" in args.problem_ids
    assert "P3JAVA" in args.problem_ids
    assert "P4" in args.problem_ids
    assert "P5" in args.problem_ids


def test_max_parallel_default_and_override() -> None:
    args = CLIArgsParser().parse(["--sweep", "--max-parallel", "8"])
    assert args.max_parallel == 8


def test_no_problem_arg_errors_out() -> None:
    with pytest.raises(SystemExit):
        CLIArgsParser().parse([])


def test_model_override_is_captured() -> None:
    args = CLIArgsParser().parse([
        "--problem", "P0", "--model-override", "claude-haiku-4-5-20251001",
    ])
    assert args.model_override == "claude-haiku-4-5-20251001"


def test_seed_default_is_zero() -> None:
    args = CLIArgsParser().parse(["--problem", "P0"])
    assert args.seed == 0
    assert args.deterministic is False
    assert args.temperature_architect is None
    assert args.temperature_icp is None


def test_seed_and_deterministic_flags() -> None:
    args = CLIArgsParser().parse([
        "--problem", "P0", "--seed", "7", "--deterministic",
    ])
    assert args.seed == 7
    assert args.deterministic is True


def test_temperature_overrides_parsed() -> None:
    args = CLIArgsParser().parse([
        "--problem", "P0",
        "--temperature-architect", "0.1",
        "--temperature-icp", "0.5",
    ])
    assert args.temperature_architect == 0.1
    assert args.temperature_icp == 0.5


def test_retry_and_budget_flags_default() -> None:
    args = CLIArgsParser().parse(["--problem", "P0"])
    assert args.max_icp_retries == 1
    assert args.max_fixer_passes == 1
    assert args.retry_backoff_base == 1.0
    assert args.max_cost_usd is None
    assert args.warn_cost_pct == 0.8


def test_retry_and_budget_flags_overridden() -> None:
    args = CLIArgsParser().parse([
        "--problem", "P0",
        "--max-icp-retries", "3",
        "--max-fixer-passes", "2",
        "--retry-backoff-base", "0.5",
        "--max-cost-usd", "1.25",
        "--warn-cost-pct", "0.9",
    ])
    assert args.max_icp_retries == 3
    assert args.max_fixer_passes == 2
    assert args.retry_backoff_base == 0.5
    assert args.max_cost_usd == 1.25
    assert args.warn_cost_pct == 0.9


def test_p0go_id_resolves_to_go_problem_spec() -> None:
    args = CLIArgsParser().parse(["--problem", "P0GO"])
    assert args.problem_ids == ("P0GO",)
    spec = ProblemResolver().resolve("P0GO")
    assert spec.id == "P0GO"
    assert spec.target_language is TargetLanguage.GO
    assert spec.slug == "calculator"


def test_p0rust_id_resolves_to_rust_problem_spec() -> None:
    args = CLIArgsParser().parse(["--problem", "P0RUST"])
    assert args.problem_ids == ("P0RUST",)
    spec = ProblemResolver().resolve("P0RUST")
    assert spec.id == "P0RUST"
    assert spec.target_language is TargetLanguage.RUST
    assert spec.slug == "calculator"


def test_infra_flag_defaults_to_manual() -> None:
    args = CLIArgsParser().parse(["--problem", "P0"])
    assert args.infrastructure_mode == "manual"


def test_infra_flag_accepts_auto() -> None:
    args = CLIArgsParser().parse(["--problem", "P0", "--infra", "auto"])
    assert args.infrastructure_mode == "auto"


def test_infra_flag_rejects_unknown_value() -> None:
    with pytest.raises(SystemExit):
        CLIArgsParser().parse(["--problem", "P0", "--infra", "magic"])


def test_squib_file_is_a_valid_standalone_input() -> None:
    args = CLIArgsParser().parse(["--squib-file", "out/recovered.squib"])
    assert args.squib_file == "out/recovered.squib"
    assert args.problem_ids == ()


def test_legacy_tests_flag_is_parsed() -> None:
    args = CLIArgsParser().parse(
        ["--squib-file", "r.squib", "--legacy-tests", "legacy/tests"],
    )
    assert args.legacy_tests == "legacy/tests"


def test_no_input_mode_is_rejected() -> None:
    with pytest.raises(SystemExit):
        CLIArgsParser().parse([])


def test_recover_from_is_a_valid_standalone_input() -> None:
    args = CLIArgsParser().parse(["--recover-from", "some/project"])
    assert args.recover_from == "some/project"
    assert args.problem_ids == ()


def test_criteria_are_parsed_in_order() -> None:
    args = CLIArgsParser().parse(
        ["--recover-from", "p", "--criteria", "testability, simplicity ,performance"],
    )
    assert args.criteria == ("testability", "simplicity", "performance")


def test_recover_out_flag_is_parsed() -> None:
    args = CLIArgsParser().parse(
        ["--recover-from", "p", "--recover-out", "out/x.squib"],
    )
    assert args.recover_out == "out/x.squib"


def test_triage_is_a_valid_standalone_input() -> None:
    args = CLIArgsParser().parse(["--triage", "out/violations.json"])
    assert args.triage == "out/violations.json"
    assert args.problem_ids == ()


def test_refactor_and_plan_flags_are_parsed() -> None:
    args = CLIArgsParser().parse(
        ["--refactor", "recovered.squib", "--plan", "refactor_plan.json"],
    )
    assert args.refactor == "recovered.squib"
    assert args.plan == "refactor_plan.json"


def test_refactor_is_a_valid_standalone_input() -> None:
    args = CLIArgsParser().parse(["--refactor", "recovered.squib"])
    assert args.refactor == "recovered.squib"
    assert args.problem_ids == ()
