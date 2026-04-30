"""Tests for ModuleImplementationSerializer round-trip (G3)."""

from squeaky_clean.application.dtos.implemented_class import ImplementedClass
from squeaky_clean.application.dtos.module_implementation import ModuleImplementation
from squeaky_clean.application.use_cases.module_implementation_serializer import (
    ModuleImplementationSerializer,
)
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType


def _impls() -> tuple[ModuleImplementation, ...]:
    cls = ClassSpec(
        name="Operand", pattern="ValueObject", implements=None,
        methods=(), depends=(), concretes=(),
    )
    mod = ModuleSpec(
        name="Calc", layer=LayerType.DOMAIN, exports=(), depends=(),
        classes=(cls,), invariants=(),
    )
    ic = ImplementedClass(
        class_name="Operand", file_path="src/operand.py",
        code="class Operand: pass\n", test_code="def test_x(): pass\n",
        cost_usd=0.01, duration_ms=120, input_tokens=10, output_tokens=20,
        retries=1,
    )
    impl = ModuleImplementation(
        module=mod, implemented_classes=(ic,), total_cost_usd=0.01,
        total_duration_ms=120, total_input_tokens=10, total_output_tokens=20,
        wall_duration_ms=120, total_retries=1,
    )
    return (impl,)


def test_round_trip_preserves_equality() -> None:
    impls = _impls()
    ser = ModuleImplementationSerializer()
    assert ser.deserialize(ser.serialize(impls)) == impls
