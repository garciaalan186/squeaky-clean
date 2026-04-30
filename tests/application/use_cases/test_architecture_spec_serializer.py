"""Tests for ArchitectureSpecSerializer round-trip (G3)."""

from squeaky_clean.application.use_cases.architecture_spec_serializer import (
    ArchitectureSpecSerializer,
)
from squeaky_clean.domain.entities.architecture_graph import ArchitectureGraph
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType


def _spec() -> ArchitectureSpec:
    cls = ClassSpec(
        name="Order", pattern="Entity", implements=None,
        methods=("validate(): Result",), depends=("Money",),
        concretes=(), fields=("amount: Money",), invariants=("amount > 0",),
    )
    mod = ModuleSpec(
        name="Sales", layer=LayerType.DOMAIN, exports=("OrderRepo",),
        depends=("SharedKernel::Money",), classes=(cls,),
        invariants=("orders are immutable",),
    )
    return ArchitectureSpec(
        modules=(mod,), graph=ArchitectureGraph(edges={"Sales": ("Shared",)}),
    )


def test_round_trip_preserves_equality() -> None:
    s = _spec()
    ser = ArchitectureSpecSerializer()
    assert ser.deserialize(ser.serialize(s)) == s


def test_serialize_emits_valid_json() -> None:
    import json
    payload = ArchitectureSpecSerializer().serialize(_spec())
    parsed = json.loads(payload)
    assert parsed["modules"][0]["name"] == "Sales"
    assert parsed["edges"]["Sales"] == ["Shared"]
