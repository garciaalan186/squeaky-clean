"""Tests for MicroEvalCommand wiring (R5.4) — no LLM calls."""

from pathlib import Path

from squeaky_clean.interface.cli.micro_eval_command import MicroEvalCommand


def test_command_is_constructible() -> None:
    assert MicroEvalCommand() is not None


def test_select_without_patterns_keeps_everything() -> None:
    fixtures = [Path("a/strategy.squib"), Path("a/state.squib")]
    assert MicroEvalCommand.select(fixtures, ()) == fixtures


def test_select_filters_by_stem_prefix() -> None:
    fixtures = [
        Path("a/strategy_depends_shape.squib"),
        Path("a/state.squib"),
        Path("a/visitor.squib"),
    ]
    kept = MicroEvalCommand.select(fixtures, ("strategy", "visitor"))
    assert [f.stem for f in kept] == ["strategy_depends_shape", "visitor"]
