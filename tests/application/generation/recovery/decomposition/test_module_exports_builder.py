"""Tests for ModuleExportsBuilder: cross-module dependency -> EXPORTS."""

from squeaky_clean.application.generation.recovery.decomposition.module_exports_builder import (
    ModuleExportsBuilder,
)
from squeaky_clean.application.generation.recovery.extraction.class_catalog import ClassCatalog


def _catalog(graph: dict[str, tuple[str, ...]]) -> ClassCatalog:
    return ClassCatalog(classes=(), import_graph=graph)


def test_cross_module_dep_exports_target_from_its_own_module() -> None:
    catalog = _catalog({"shop.app.Service": ("shop.a.Order",)})
    module_of = {"shop.app.Service": "App", "shop.a.Order": "Order"}
    exports = ModuleExportsBuilder().build(catalog, module_of)
    assert exports == {"Order": ("Order",)}


def test_intra_module_and_unassigned_deps_export_nothing() -> None:
    catalog = _catalog({
        "shop.a.Order": ("shop.a.LineItem",),      # same module
        "shop.app.Service": ("thirdparty.Client",),  # not in module_of
    })
    module_of = {"shop.a.Order": "Order", "shop.a.LineItem": "Order",
                 "shop.app.Service": "App"}
    assert ModuleExportsBuilder().build(catalog, module_of) == {}


def test_repeated_deps_are_deduplicated_in_first_seen_order() -> None:
    catalog = _catalog({
        "shop.app.Service": ("shop.a.Order", "shop.a.LineItem"),
        "shop.api.Controller": ("shop.a.Order",),
    })
    module_of = {"shop.app.Service": "App", "shop.api.Controller": "Web",
                 "shop.a.Order": "Order", "shop.a.LineItem": "Order"}
    exports = ModuleExportsBuilder().build(catalog, module_of)
    assert exports == {"Order": ("Order", "LineItem")}
