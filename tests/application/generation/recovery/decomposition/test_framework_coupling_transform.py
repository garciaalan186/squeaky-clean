"""Tests for FrameworkCouplingTransform: 1->N split of coupled classes."""

from squeaky_clean.application.generation.recovery.decomposition.framework_coupling_transform import (
    FrameworkCouplingTransform,
)
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType


def _cls(name: str) -> ClassSpec:
    return ClassSpec(
        name=name, pattern="SimpleClass", implements=None,
        methods=(), depends=(), concretes=(),
    )


def _spec() -> ArchitectureSpec:
    module = ModuleSpec(
        name="Orders", layer=LayerType.DOMAIN, exports=("Order",),
        depends=(), classes=(_cls("Order"), _cls("LineItem")), invariants=(),
    )
    return ArchitectureSpec.single(module)


def test_target_splits_into_entity_plus_repository_and_both_are_exported() -> None:
    result = FrameworkCouplingTransform().apply(_spec(), frozenset({"Order"}))
    domain = result.modules[0]
    assert [(c.name, c.pattern) for c in domain.classes] == [
        ("Order", "Entity"), ("OrderRepository", "Repository"), ("LineItem", "SimpleClass"),
    ]
    assert domain.exports == ("Order", "OrderRepository")


def test_adapter_moves_to_companion_infra_module_with_inward_edge() -> None:
    result = FrameworkCouplingTransform().apply(_spec(), frozenset({"Order"}))
    infra = result.modules[1]
    assert infra.name == "OrdersInfra"
    assert infra.layer is LayerType.INFRASTRUCTURE
    assert [c.name for c in infra.classes] == ["OrderAdapter"]
    assert infra.depends == ("Orders::Order", "Orders::OrderRepository")
    assert result.graph.edges["OrdersInfra"] == ("Orders",)


def test_no_targets_keeps_module_untouched_and_adds_no_infra_module() -> None:
    result = FrameworkCouplingTransform().apply(_spec(), frozenset())
    assert result.modules == _spec().modules
    assert "OrdersInfra" not in result.graph.edges
