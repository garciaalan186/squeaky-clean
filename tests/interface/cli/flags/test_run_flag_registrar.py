"""Tests for RunFlagRegistrar (problem selection + run shape)."""

from squeaky_clean.interface.cli.cli_args_parser import CLIArgsParser


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


def test_model_override_is_captured() -> None:
    args = CLIArgsParser().parse([
        "--problem", "P0", "--model-override", "claude-haiku-4-5-20251001",
    ])
    assert args.model_override == "claude-haiku-4-5-20251001"


def test_replicates_and_problem_file_parsed() -> None:
    args = CLIArgsParser().parse([
        "--problem-file", "spec.json", "--replicates", "3",
    ])
    assert args.problem_file == "spec.json"
    assert args.replicates == 3
