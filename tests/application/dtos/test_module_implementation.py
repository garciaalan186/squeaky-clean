"""Tests for ModuleImplementation DTO."""

from dataclasses import FrozenInstanceError

import pytest

from squeaky_clean.application.dtos.implemented_class import ImplementedClass
from squeaky_clean.application.dtos.module_implementation import ModuleImplementation
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType


def _module() -> ModuleSpec:
    return ModuleSpec(
        name="Calculator",
        layer=LayerType.DOMAIN,
        exports=("Operand",),
        depends=(),
        classes=(
            ClassSpec(
                name="Operand",
                pattern="ValueObject",
                implements=None,
                methods=(),
                depends=(),
                concretes=(),
            ),
        ),
        invariants=(),
    )


def _impl() -> ImplementedClass:
    return ImplementedClass(
        class_name="Operand",
        file_path="src/operand.py",
        code="class Operand: pass",
        test_code=None,
        cost_usd=0.05,
        duration_ms=500,
        input_tokens=80,
        output_tokens=40,
    )


def test_construction_preserves_fields() -> None:
    mi = ModuleImplementation(
        module=_module(),
        implemented_classes=(_impl(),),
        total_cost_usd=0.05,
        total_duration_ms=500,
        total_input_tokens=80,
        total_output_tokens=40,
    wall_duration_ms=0,
    )
    assert len(mi.implemented_classes) == 1
    assert mi.total_cost_usd == 0.05
    assert mi.total_input_tokens == 80
    assert mi.total_output_tokens == 40


def test_frozen_behavior() -> None:
    mi = ModuleImplementation(
        module=_module(),
        implemented_classes=(),
        total_cost_usd=0.0,
        total_duration_ms=0,
        total_input_tokens=0,
        total_output_tokens=0,
    wall_duration_ms=0,
    )
    with pytest.raises(FrozenInstanceError):
        mi.total_cost_usd = 1.0  # type: ignore[misc]
