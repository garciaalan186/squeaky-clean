"""Tests for ModuleGraphBuilder: cross-module DEPENDS + module DAG edges."""

from squeaky_clean.application.generation.recovery.decomposition.module_graph_builder import (
    ModuleGraphBuilder,
)
from squeaky_clean.application.generation.recovery.extraction.class_catalog import ClassCatalog


def _catalog(graph: dict[str, tuple[str, ...]]) -> ClassCatalog:
    return ClassCatalog(classes=(), import_graph=graph)


def test_cross_module_edge_yields_depends_entry_and_dag_edge() -> None:
    catalog = _catalog({"a.Order": ("b.Money",), "b.Money": ()})
    module_of = {"a.Order": "Orders", "b.Money": "Shared"}
    depends, edges = ModuleGraphBuilder().build(catalog, module_of)
    assert depends == {"Orders": ("Shared::Money",)}
    assert edges == {"Orders": ("Shared",), "Shared": ()}


def test_same_module_edges_are_not_depends() -> None:
    catalog = _catalog({"a.Order": ("a.LineItem",), "a.LineItem": ()})
    module_of = {"a.Order": "Orders", "a.LineItem": "Orders"}
    depends, edges = ModuleGraphBuilder().build(catalog, module_of)
    assert depends == {}
    assert edges == {"Orders": ()}


def test_unknown_targets_are_ignored_and_entries_deduplicated() -> None:
    catalog = _catalog({
        "a.Order": ("b.Money", "b.Money", "x.Ghost"),
        "b.Money": (),
    })
    module_of = {"a.Order": "Orders", "b.Money": "Shared"}
    depends, edges = ModuleGraphBuilder().build(catalog, module_of)
    assert depends["Orders"] == ("Shared::Money",)
    assert edges["Orders"] == ("Shared",)


def test_every_module_is_keyed_in_the_edge_map() -> None:
    catalog = _catalog({"a.A": (), "b.B": ()})
    module_of = {"a.A": "Alpha", "b.B": "Beta"}
    _, edges = ModuleGraphBuilder().build(catalog, module_of)
    assert edges == {"Alpha": (), "Beta": ()}
