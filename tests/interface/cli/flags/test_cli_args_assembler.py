"""Tests for CLIArgsAssembler (Namespace -> CLIArgs conversion)."""

from squeaky_clean.interface.cli.cli_args_parser import CLIArgsParser


def test_optional_fields_default_to_none() -> None:
    args = CLIArgsParser().parse(["--problem", "P0"])
    assert args.model_override is None
    assert args.problem_file is None
    assert args.max_cost_usd is None
    assert args.resume_run_dir is None
    assert args.squib_file is None
    assert args.recover_from is None
    assert args.triage is None
    assert args.refactor is None
    assert args.plan is None
    assert args.refactor_out is None


def test_csv_fields_strip_whitespace_and_drop_empties() -> None:
    args = CLIArgsParser().parse([
        "--problem", "P0",
        "--prompt-cache-tiers", " architect ,, icp ",
    ])
    assert args.prompt_cache_tiers == ("architect", "icp")


def test_criteria_default_is_empty_tuple() -> None:
    assert CLIArgsParser().parse(["--problem", "P0"]).criteria == ()


def test_numeric_coercions_round_trip() -> None:
    args = CLIArgsParser().parse([
        "--problem", "P0", "--seed", "3", "--max-cost-usd", "2.5",
    ])
    assert args.seed == 3
    assert args.max_cost_usd == 2.5
