"""Tests for InfraFlagRegistrar (infra mode, techspec TTL, wiring toggles)."""

import pytest

from squeaky_clean.interface.cli.cli_args_parser import CLIArgsParser


def test_infra_flag_defaults_to_manual() -> None:
    args = CLIArgsParser().parse(["--problem", "P0"])
    assert args.infrastructure_mode == "manual"


def test_infra_flag_accepts_auto() -> None:
    args = CLIArgsParser().parse(["--problem", "P0", "--infra", "auto"])
    assert args.infrastructure_mode == "auto"


def test_infra_flag_rejects_unknown_value() -> None:
    with pytest.raises(SystemExit):
        CLIArgsParser().parse(["--problem", "P0", "--infra", "magic"])


def test_infer_infrastructure_defaults_off() -> None:
    args = CLIArgsParser().parse(["--problem", "P0"])
    assert args.infer_infrastructure is False
    assert CLIArgsParser().parse(
        ["--problem", "P0", "--infer-infrastructure"],
    ).infer_infrastructure is True


def test_techspec_cache_ttl_default_and_override() -> None:
    assert CLIArgsParser().parse(["--problem", "P0"]).techspec_cache_ttl_days == 30
    args = CLIArgsParser().parse(["--problem", "P0", "--techspec-cache-ttl-days", "7"])
    assert args.techspec_cache_ttl_days == 7


def test_emit_wiring_default_on_and_no_flag_disables() -> None:
    assert CLIArgsParser().parse(["--problem", "P0"]).emit_wiring is True
    assert CLIArgsParser().parse(["--problem", "P0", "--no-emit-wiring"]).emit_wiring is False
