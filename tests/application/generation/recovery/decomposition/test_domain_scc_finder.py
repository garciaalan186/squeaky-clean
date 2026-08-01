"""Tests for DomainSCCFinder: SCCs of the DOMAIN-layer import subgraph."""

from squeaky_clean.application.generation.recovery.decomposition.domain_scc_finder import (
    DomainSCCFinder,
)
from squeaky_clean.application.generation.recovery.extraction.class_catalog import ClassCatalog
from squeaky_clean.domain.value_objects.layer_type import LayerType


def _catalog(graph: dict[str, tuple[str, ...]]) -> ClassCatalog:
    return ClassCatalog(classes=(), import_graph=graph)


def test_acyclic_domain_yields_sorted_singleton_components() -> None:
    catalog = _catalog({"a.Order": ("a.LineItem",), "a.LineItem": ()})
    layers = {"a.Order": LayerType.DOMAIN, "a.LineItem": LayerType.DOMAIN}
    components = DomainSCCFinder().components(catalog, layers)
    assert sorted(components) == [("a.LineItem",), ("a.Order",)]
    assert all(len(comp) == 1 for comp in components)


def test_mutual_imports_collapse_into_one_sorted_component() -> None:
    catalog = _catalog({
        "a.Order": ("a.Invoice",), "a.Invoice": ("a.Order",), "a.Money": (),
    })
    layers = {fqn: LayerType.DOMAIN for fqn in ("a.Order", "a.Invoice", "a.Money")}
    components = DomainSCCFinder().components(catalog, layers)
    assert ("a.Invoice", "a.Order") in components
    assert ("a.Money",) in components
    assert len(components) == 2


def test_non_domain_classes_and_edges_are_excluded() -> None:
    catalog = _catalog({
        "a.Order": ("infra.OrderRepo",),
        "infra.OrderRepo": ("a.Order",),
    })
    layers = {"a.Order": LayerType.DOMAIN,
              "infra.OrderRepo": LayerType.INFRASTRUCTURE}
    components = DomainSCCFinder().components(catalog, layers)
    assert components == (("a.Order",),)


def test_same_catalog_always_yields_the_same_component_order() -> None:
    catalog = _catalog({"a.B": ("a.A",), "a.A": ("a.B",), "a.C": ("a.A",)})
    layers = {fqn: LayerType.DOMAIN for fqn in ("a.A", "a.B", "a.C")}
    first = DomainSCCFinder().components(catalog, layers)
    second = DomainSCCFinder().components(catalog, layers)
    assert first == second == (("a.A", "a.B"), ("a.C",))
