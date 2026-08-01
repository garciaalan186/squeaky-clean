"""Tests for the ModuleAssignment DTO: field carriage, immutability, equality."""

from dataclasses import FrozenInstanceError

import pytest

from squeaky_clean.application.generation.recovery.decomposition.module_assignment import (
    ModuleAssignment,
)
from squeaky_clean.domain.value_objects.layer_type import LayerType


def test_carries_module_and_layer_maps_verbatim() -> None:
    assignment = ModuleAssignment(
        module_of={"shop.a.Order": "Order"},
        layer_of={"Order": LayerType.DOMAIN})
    assert assignment.module_of["shop.a.Order"] == "Order"
    assert assignment.layer_of["Order"] is LayerType.DOMAIN


def test_is_frozen_against_field_reassignment() -> None:
    assignment = ModuleAssignment(module_of={}, layer_of={})
    with pytest.raises(FrozenInstanceError):
        assignment.module_of = {"x": "y"}  # type: ignore[misc]


def test_value_equality_follows_field_contents() -> None:
    left = ModuleAssignment(module_of={"a.B": "B"},
                            layer_of={"B": LayerType.DOMAIN})
    right = ModuleAssignment(module_of={"a.B": "B"},
                             layer_of={"B": LayerType.DOMAIN})
    other = ModuleAssignment(module_of={"a.B": "B"},
                             layer_of={"B": LayerType.APPLICATION})
    assert left == right
    assert left != other
