"""Tests for SecurityCacheFlagRegistrar (SAST, security tests, prompt cache)."""

import pytest

from squeaky_clean.interface.cli.cli_args_parser import CLIArgsParser


def test_security_flags_default_off() -> None:
    args = CLIArgsParser().parse(["--problem", "P0"])
    assert args.enable_sast is False
    assert args.enable_security_tests is False


def test_security_flags_opt_in() -> None:
    args = CLIArgsParser().parse([
        "--problem", "P0", "--enable-sast", "--security-tests",
    ])
    assert args.enable_sast is True
    assert args.enable_security_tests is True


def test_prompt_cache_defaults_on_with_all_tiers() -> None:
    args = CLIArgsParser().parse(["--problem", "P0"])
    assert args.prompt_cache is True
    assert args.prompt_cache_tiers == ("architect", "manager", "icp", "fixer")


def test_no_prompt_cache_disables_cache() -> None:
    args = CLIArgsParser().parse(["--problem", "P0", "--no-prompt-cache"])
    assert args.prompt_cache is False


def test_prompt_cache_tiers_csv_is_parsed() -> None:
    args = CLIArgsParser().parse([
        "--problem", "P0", "--prompt-cache-tiers", "architect, icp",
    ])
    assert args.prompt_cache_tiers == ("architect", "icp")


def test_architect_mode_default_and_choices() -> None:
    assert CLIArgsParser().parse(["--problem", "P0"]).architect_mode == "patterned"
    args = CLIArgsParser().parse(["--problem", "P0", "--architect-mode", "scoped"])
    assert args.architect_mode == "scoped"
    with pytest.raises(SystemExit):
        CLIArgsParser().parse(["--problem", "P0", "--architect-mode", "bogus"])
