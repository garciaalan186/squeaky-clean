"""Tests for CustomPatternManifestEntry validation."""

import pytest

from squeaky_clean.application.shared.problem.custom_pattern_manifest_entry import (
    CustomPatternManifestEntry,
)


def test_valid_entry() -> None:
    e = CustomPatternManifestEntry(
        name="EventSourcedAggregate",
        emitter_spec_name="python/custom/EventSourcedAggregateEmitter",
    )
    assert e.name == "EventSourcedAggregate"


def test_rejects_empty_name() -> None:
    with pytest.raises(ValueError, match="name is empty"):
        CustomPatternManifestEntry(name=" ", emitter_spec_name="x")


def test_rejects_empty_emitter_spec_name() -> None:
    with pytest.raises(ValueError, match="emitter_spec_name is empty"):
        CustomPatternManifestEntry(name="X", emitter_spec_name="")
