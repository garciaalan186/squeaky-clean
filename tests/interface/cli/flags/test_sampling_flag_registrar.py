"""Tests for SamplingFlagRegistrar (sampling, retry, and budget flags)."""

from squeaky_clean.interface.cli.cli_args_parser import CLIArgsParser


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
