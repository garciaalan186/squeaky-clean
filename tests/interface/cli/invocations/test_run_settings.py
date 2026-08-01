"""Tests for RunSettings (R6.5)."""

import dataclasses

import pytest

from squeaky_clean.interface.cli.invocations.run_settings import RunSettings


def test_defaults() -> None:
    s = RunSettings()
    assert s.seed == 0
    assert s.deterministic is False
    assert s.replay_only is False
    assert s.architect_mode == "patterned"
    assert s.retry.max_icp_retries == 1
    assert s.infra.infrastructure_mode == "manual"


def test_is_frozen() -> None:
    with pytest.raises(dataclasses.FrozenInstanceError):
        RunSettings().seed = 1  # type: ignore[misc]


def test_reseeding_via_replace_keeps_other_fields() -> None:
    s = dataclasses.replace(RunSettings(architect_mode="free"), seed=3)
    assert s.seed == 3
    assert s.architect_mode == "free"


def test_stays_within_isp_field_budget() -> None:
    assert len(dataclasses.fields(RunSettings)) <= 12
