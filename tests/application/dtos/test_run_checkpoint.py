"""Tests for the RunCheckpoint DTO (G3 resumable runs)."""

import pytest

from squeaky_clean.application.dtos.run_checkpoint import RunCheckpoint


def test_defaults_are_started_or_empty() -> None:
    cp = RunCheckpoint()
    assert cp.version == "v1"
    assert cp.stage == ""
    assert cp.checksum == ""
    assert cp.cost_spent_usd == 0.0


def test_accepts_every_known_stage() -> None:
    for stage in ("started", "architect_done", "test_arch_done", "icps_done",
                  "integrated", "tested", "fixed", "complete"):
        assert RunCheckpoint(stage=stage).stage == stage


def test_rejects_unknown_stage() -> None:
    with pytest.raises(ValueError, match="invalid stage"):
        RunCheckpoint(stage="zzz")


def test_rejects_unknown_version() -> None:
    with pytest.raises(ValueError, match="unsupported checkpoint version"):
        RunCheckpoint(version="v9999")
