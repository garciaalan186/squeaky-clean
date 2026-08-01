"""Tests for CleanSplitFactory: Entity/Repository/Adapter triple generation."""

from squeaky_clean.application.generation.recovery.decomposition.clean_split_factory import (
    CleanSplitFactory,
)
from squeaky_clean.domain.entities.class_spec import ClassSpec

_COUPLED = ClassSpec(
    name="Order", pattern="SimpleClass", implements=None,
    methods=("total(): int",), depends=("LineItem",), concretes=(),
    fields=("id: str",), invariants=("total is non-negative",),
)


def test_entity_keeps_original_members_but_retypes_to_entity() -> None:
    entity = CleanSplitFactory().entity(_COUPLED)
    assert entity.name == "Order"
    assert entity.pattern == "Entity"
    assert entity.implements is None
    assert entity.methods == ("total(): int",)
    assert entity.depends == ("LineItem",)
    assert entity.fields == ("id: str",)
    assert entity.invariants == ("total is non-negative",)


def test_repository_is_a_crud_port_depending_on_the_entity() -> None:
    repo = CleanSplitFactory().repository(_COUPLED)
    assert repo.name == "OrderRepository"
    assert repo.pattern == "Repository"
    assert repo.methods == ("save(order: Order): None", "find_by_id(id: str): Order")
    assert repo.depends == ("Order",)
    assert repo.fields == () and repo.invariants == ()


def test_adapter_implements_the_port_with_module_qualified_deps() -> None:
    adapter = CleanSplitFactory().adapter(_COUPLED, "Orders")
    assert adapter.name == "OrderAdapter"
    assert adapter.pattern == "Adapter"
    assert adapter.implements == "OrderRepository"
    assert adapter.depends == ("Orders::Order", "Orders::OrderRepository")
    assert adapter.methods == CleanSplitFactory().repository(_COUPLED).methods
