"""Tests for MicroEvalCommand wiring (R5.4) — no LLM calls."""

from squeaky_clean.interface.cli.micro_eval_command import MicroEvalCommand


def test_command_is_constructible() -> None:
    assert MicroEvalCommand() is not None
