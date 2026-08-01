"""Tests for RecoveryInvocation (R6.5)."""

import dataclasses

import pytest

from squeaky_clean.interface.cli.invocations.recovery_invocation import RecoveryInvocation


def test_defaults() -> None:
    inv = RecoveryInvocation()
    assert inv.squib_file is None
    assert inv.recover_from is None
    assert inv.recover_language == "python"
    assert inv.criteria == ()
    assert inv.triage is None
    assert inv.refactor is None
    assert inv.plan is None


def test_is_frozen() -> None:
    with pytest.raises(dataclasses.FrozenInstanceError):
        RecoveryInvocation().triage = "x"  # type: ignore[misc]


def test_stays_within_isp_field_budget() -> None:
    assert len(dataclasses.fields(RecoveryInvocation)) <= 12
