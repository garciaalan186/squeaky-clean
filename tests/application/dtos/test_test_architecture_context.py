"""Tests for TestArchitectureContext DTO."""

from dataclasses import FrozenInstanceError

import pytest

from eval.problems.p0_calculator import P0
from squeaky_clean.application.dtos.test_architecture_context import TestArchitectureContext
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType


def _module() -> ModuleSpec:
    return ModuleSpec(
        name="Calculator",
        layer=LayerType.DOMAIN,
        exports=("Calculator",),
        depends=(),
        classes=(
            ClassSpec(
                name="Calculator",
                pattern="SimpleClass",
                implements=None,
                methods=("add(a: int, b: int): int",),
                depends=(),
                concretes=(),
            ),
        ),
        invariants=(),
    )


def test_construction_preserves_fields() -> None:
    ctx = TestArchitectureContext(module=_module(), problem=P0)
    assert ctx.module.name == "Calculator"
    assert ctx.problem.id == "P0"


def test_frozen_behavior() -> None:
    ctx = TestArchitectureContext(module=_module(), problem=P0)
    with pytest.raises(FrozenInstanceError):
        ctx.problem = P0  # type: ignore[misc]
