"""Tests for EntityLifecycle DTO."""

import pytest

from squeaky_clean.application.dtos.entity_lifecycle import EntityLifecycle, StateTransition


def test_entity_lifecycle_round_trip() -> None:
    t = StateTransition(from_state="draft", to_state="published", trigger="publish")
    el = EntityLifecycle(entity="Tweet", transitions=(t,))
    assert el.entity == "Tweet"
    assert el.transitions[0].trigger == "publish"


def test_state_transition_rejects_empty_field() -> None:
    with pytest.raises(ValueError, match="non-empty"):
        StateTransition(from_state="", to_state="x", trigger="t")


def test_entity_lifecycle_rejects_empty_entity() -> None:
    t = StateTransition(from_state="a", to_state="b", trigger="c")
    with pytest.raises(ValueError, match="non-empty"):
        EntityLifecycle(entity="", transitions=(t,))


def test_entity_lifecycle_rejects_empty_transitions() -> None:
    with pytest.raises(ValueError, match="at least one"):
        EntityLifecycle(entity="Tweet", transitions=())
