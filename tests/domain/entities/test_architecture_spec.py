"""Unit tests for ArchitectureSpec multi-module aggregation."""

from squeaky_clean.domain.entities.architecture_graph import ArchitectureGraph
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType


def _module(name: str) -> ModuleSpec:
    cls = ClassSpec(
        name=f"{name}Class", pattern="SimpleClass",
        fields=(), methods=(), depends=(), concretes=(), invariants=(),
        implements=None,
    )
    return ModuleSpec(
        name=name, layer=LayerType.DOMAIN,
        exports=(f"{name}Class",), depends=(),
        classes=(cls,), invariants=(),
    )


def test_single_module_factory_validates() -> None:
    spec = ArchitectureSpec.single(_module("Cart"))
    assert spec.validate() == ()


def test_two_independent_modules_validate() -> None:
    spec = ArchitectureSpec(
        modules=(_module("Cart"), _module("Catalog")),
        graph=ArchitectureGraph(edges={}),
    )
    assert spec.validate() == ()


def test_unknown_module_in_graph_flagged() -> None:
    spec = ArchitectureSpec(
        modules=(_module("Cart"),),
        graph=ArchitectureGraph(edges={"Cart": ("Catalog",)}),
    )
    issues = spec.validate()
    assert any("Catalog" in v for v in issues)


def test_cycle_flagged() -> None:
    spec = ArchitectureSpec(
        modules=(_module("Cart"), _module("Catalog")),
        graph=ArchitectureGraph(edges={
            "Cart": ("Catalog",), "Catalog": ("Cart",),
        }),
    )
    issues = spec.validate()
    assert any("cycle" in v for v in issues)


def test_empty_modules_flagged() -> None:
    spec = ArchitectureSpec(
        modules=(),
        graph=ArchitectureGraph(edges={}),
    )
    assert any("no modules" in v for v in spec.validate())
