"""Tests for MicroEvalInvocation (R6.5)."""

import dataclasses

import pytest

from squeaky_clean.interface.cli.invocations.micro_eval_invocation import MicroEvalInvocation


def test_defaults() -> None:
    inv = MicroEvalInvocation()
    assert inv.enabled is False
    assert inv.model_override is None
    assert inv.settings.seed == 0


def test_is_frozen() -> None:
    with pytest.raises(dataclasses.FrozenInstanceError):
        MicroEvalInvocation().enabled = True  # type: ignore[misc]


def test_stays_within_isp_field_budget() -> None:
    assert len(dataclasses.fields(MicroEvalInvocation)) <= 12
