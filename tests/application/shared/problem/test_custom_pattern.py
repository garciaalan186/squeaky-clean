"""Tests for the CustomPattern value object."""

import pytest

from squeaky_clean.application.shared.problem.custom_pattern import CustomPattern


def test_holds_name_and_spec_stem() -> None:
    p = CustomPattern(name="EventSourcedAggregate",
                      emitter_spec_name="python/custom/EventSourcedAggregateEmitter")
    assert p.name == "EventSourcedAggregate"
    assert p.emitter_spec_name.endswith("EventSourcedAggregateEmitter")


def test_is_frozen() -> None:
    p = CustomPattern(name="X", emitter_spec_name="y")
    with pytest.raises(AttributeError):
        p.name = "Z"  # type: ignore[misc]
