"""Tests for JavaScriptClassCatalogExtractor: *.js-scoped ES extraction."""

from pathlib import Path

from squeaky_clean.application.generation.recovery.extraction.javascript_catalog_extractor import (
    JavaScriptClassCatalogExtractor,
)


def test_only_js_files_are_catalogued(tmp_path: Path) -> None:
    (tmp_path / "user.js").write_text("export class User {}\n")
    (tmp_path / "order.ts").write_text("export class Order {}\n")
    catalog = JavaScriptClassCatalogExtractor().extract(tmp_path)
    assert tuple(r.fqn for r in catalog.classes) == ("user.User",)


def test_fqn_is_path_derived_and_nested_dirs_walk(tmp_path: Path) -> None:
    sub = tmp_path / "src" / "domain"
    sub.mkdir(parents=True)
    (sub / "cart.js").write_text("class Cart extends Base {}\n")
    catalog = JavaScriptClassCatalogExtractor().extract(tmp_path)
    record = catalog.classes[0]
    assert record.fqn == "src.domain.cart.Cart"
    assert record.bases == ("Base",)


def test_node_modules_are_out_of_ingest_scope(tmp_path: Path) -> None:
    vendored = tmp_path / "node_modules" / "lib"
    vendored.mkdir(parents=True)
    (vendored / "dep.js").write_text("export class Dep {}\n")
    (tmp_path / "app.js").write_text("export class App {}\n")
    catalog = JavaScriptClassCatalogExtractor().extract(tmp_path)
    assert tuple(r.fqn for r in catalog.classes) == ("app.App",)
