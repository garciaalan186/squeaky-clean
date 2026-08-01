"""Tests for ModuleAssigner: SCC-seeded modules + non-domain attachment."""

from squeaky_clean.application.generation.recovery.decomposition.module_assigner import (
    ModuleAssigner,
)
from squeaky_clean.application.generation.recovery.extraction.class_catalog import ClassCatalog
from squeaky_clean.application.generation.recovery.extraction.class_record import ClassRecord
from squeaky_clean.domain.value_objects.layer_type import LayerType


def _rec(fqn: str) -> ClassRecord:
    return ClassRecord(fqn=fqn, bases=(), methods=(), fields=(),
                       imports=(), decorators=())


def test_domain_scc_seeds_a_domain_module_named_after_representative() -> None:
    catalog = ClassCatalog(
        classes=(_rec("shop.a.Order"), _rec("shop.b.OrderRepo")),
        import_graph={"shop.b.OrderRepo": ("shop.a.Order",)})
    layers = {"shop.a.Order": LayerType.DOMAIN,
              "shop.b.OrderRepo": LayerType.INFRASTRUCTURE}
    result = ModuleAssigner((("shop.a.Order",),)).assign(catalog, layers)
    assert result.module_of == {"shop.a.Order": "Order", "shop.b.OrderRepo": "Order"}
    assert result.layer_of == {"Order": LayerType.DOMAIN}


def test_orphan_non_domain_class_becomes_its_own_module_in_its_layer() -> None:
    catalog = ClassCatalog(classes=(_rec("shop.api.Health"),), import_graph={})
    layers = {"shop.api.Health": LayerType.INTERFACE}
    result = ModuleAssigner().assign(catalog, layers)
    assert result.module_of == {"shop.api.Health": "Health"}
    assert result.layer_of == {"Health": LayerType.INTERFACE}


def test_non_domain_class_attaches_to_most_depended_domain_module() -> None:
    catalog = ClassCatalog(
        classes=(_rec("shop.app.Service"),),
        import_graph={"shop.app.Service": ("x.One", "y.Two", "y.Three")})
    layers = {"x.One": LayerType.DOMAIN, "y.Two": LayerType.DOMAIN,
              "y.Three": LayerType.DOMAIN,
              "shop.app.Service": LayerType.APPLICATION}
    components = (("x.One",), ("y.Two", "y.Three"))
    result = ModuleAssigner(components).assign(catalog, layers)
    assert result.module_of["shop.app.Service"] == "Two"


def test_colliding_module_names_are_deterministically_suffixed() -> None:
    catalog = ClassCatalog(classes=(), import_graph={})
    layers = {"a.Order": LayerType.DOMAIN, "b.Order": LayerType.DOMAIN}
    components = (("a.Order",), ("b.Order",))
    result = ModuleAssigner(components).assign(catalog, layers)
    assert result.module_of == {"a.Order": "Order", "b.Order": "Order2"}
    assert result.layer_of == {"Order": LayerType.DOMAIN, "Order2": LayerType.DOMAIN}
