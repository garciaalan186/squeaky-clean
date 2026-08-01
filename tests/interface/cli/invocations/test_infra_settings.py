"""Tests for InfraSettings (R6.5)."""

import dataclasses

import pytest

from squeaky_clean.interface.cli.invocations.infra_settings import InfraSettings


def test_defaults_mirror_cli_flag_defaults() -> None:
    s = InfraSettings()
    assert s.infrastructure_mode == "manual"
    assert s.infer_infrastructure is False
    assert s.techspec_cache_ttl_days == 30
    assert s.emit_wiring is True


def test_is_frozen() -> None:
    with pytest.raises(dataclasses.FrozenInstanceError):
        InfraSettings().infrastructure_mode = "auto"  # type: ignore[misc]


def test_stays_within_isp_field_budget() -> None:
    assert len(dataclasses.fields(InfraSettings)) <= 12
