"""Tests for the StateTransition DTO."""

import pytest

from squeaky_clean.application.shared.mcda.state_transition import StateTransition


def test_holds_transition_fields() -> None:
    t = StateTransition(from_state="draft", to_state="published", trigger="publish")
    assert (t.from_state, t.to_state, t.trigger) == ("draft", "published", "publish")


def test_rejects_empty_from_state() -> None:
    with pytest.raises(ValueError, match="from_state"):
        StateTransition(from_state="", to_state="x", trigger="t")


def test_rejects_empty_to_state() -> None:
    with pytest.raises(ValueError, match="to_state"):
        StateTransition(from_state="x", to_state="", trigger="t")


def test_rejects_empty_trigger() -> None:
    with pytest.raises(ValueError, match="trigger"):
        StateTransition(from_state="x", to_state="y", trigger="")
