"""Tests for RunInvocation (R6.5)."""

import dataclasses

import pytest

from squeaky_clean.interface.cli.invocations.run_invocation import RunInvocation


def test_defaults() -> None:
    inv = RunInvocation()
    assert inv.problem_ids == ()
    assert inv.problem_file is None
    assert inv.replicates == 1
    assert inv.max_parallel == 1
    assert inv.model_override is None


def test_is_frozen() -> None:
    with pytest.raises(dataclasses.FrozenInstanceError):
        RunInvocation().replicates = 2  # type: ignore[misc]


def test_stays_within_isp_field_budget() -> None:
    assert len(dataclasses.fields(RunInvocation)) <= 12
