"""Tests for MaintenanceFlagRegistrar (replay, micro-eval, dashboard, resume)."""

from squeaky_clean.interface.cli.cli_args_parser import CLIArgsParser


def test_replay_only_defaults_off_and_parses() -> None:
    assert CLIArgsParser().parse(["--problem", "P0"]).replay_only is False
    assert CLIArgsParser().parse(["--problem", "P0", "--replay-only"]).replay_only is True


def test_micro_evals_is_a_valid_standalone_input() -> None:
    args = CLIArgsParser().parse(["--micro-evals"])
    assert args.micro_evals is True
    assert args.problem_ids == ()


def test_micro_filters_default_to_empty_tuples() -> None:
    args = CLIArgsParser().parse(["--micro-evals"])
    assert args.micro_patterns == ()
    assert args.micro_languages == ()


def test_micro_filters_csv_parsed() -> None:
    args = CLIArgsParser().parse([
        "--micro-evals", "--micro-patterns", "entity, strategy",
        "--micro-languages", "go,rust",
    ])
    assert args.micro_patterns == ("entity", "strategy")
    assert args.micro_languages == ("go", "rust")


def test_rebuild_dashboard_is_a_valid_standalone_input() -> None:
    args = CLIArgsParser().parse(["--rebuild-dashboard"])
    assert args.rebuild_dashboard is True
    assert args.problem_ids == ()


def test_resume_is_a_valid_standalone_input() -> None:
    args = CLIArgsParser().parse(["--resume", "run-dir"])
    assert args.resume_run_dir == "run-dir"
    assert args.problem_ids == ()
