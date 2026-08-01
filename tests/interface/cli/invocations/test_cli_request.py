"""Tests for CLIRequest (R6.5)."""

import dataclasses

import pytest

from squeaky_clean.interface.cli.invocations.cli_request import CLIRequest
from squeaky_clean.interface.cli.invocations.run_invocation import RunInvocation


def test_defaults_compose_all_four_invocations() -> None:
    req = CLIRequest()
    assert req.run.problem_ids == ()
    assert req.recovery.squib_file is None
    assert req.micro_eval.enabled is False
    assert req.maintenance.rebuild_dashboard is False


def test_is_frozen() -> None:
    with pytest.raises(dataclasses.FrozenInstanceError):
        CLIRequest().run = RunInvocation()  # type: ignore[misc]


def test_is_a_thin_composite_not_a_bus() -> None:
    assert len(dataclasses.fields(CLIRequest)) == 4
