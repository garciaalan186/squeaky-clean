"""Tests for MaintenanceInvocation (R6.5)."""

import dataclasses

import pytest

from squeaky_clean.interface.cli.invocations.maintenance_invocation import MaintenanceInvocation


def test_defaults() -> None:
    inv = MaintenanceInvocation()
    assert inv.rebuild_dashboard is False
    assert inv.resume_run_dir is None
    assert inv.problem_ids == ()
    assert inv.problem_file is None


def test_is_frozen() -> None:
    with pytest.raises(dataclasses.FrozenInstanceError):
        MaintenanceInvocation().rebuild_dashboard = True  # type: ignore[misc]


def test_stays_within_isp_field_budget() -> None:
    assert len(dataclasses.fields(MaintenanceInvocation)) <= 12
