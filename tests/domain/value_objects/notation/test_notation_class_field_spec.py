"""Tests for NotationClassFieldSpec grammar rows."""

import dataclasses

import pytest

from squeaky_clean.domain.value_objects.notation.notation_class_field_spec import (
    NotationClassFieldSpec,
)


def test_is_frozen() -> None:
    spec = NotationClassFieldSpec("methods", "method_list")
    with pytest.raises(dataclasses.FrozenInstanceError):
        spec.name = "other"  # type: ignore[misc]


def test_carries_name_and_kind() -> None:
    spec = NotationClassFieldSpec("invariants", "invariant_list")
    assert spec.name == "invariants"
    assert spec.kind == "invariant_list"
