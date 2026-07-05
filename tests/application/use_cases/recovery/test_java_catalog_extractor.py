"""Tests for the Java catalog extractor."""

from pathlib import Path

from squeaky_clean.application.use_cases.recovery.java_catalog_extractor import (
    JavaClassCatalogExtractor,
)

_ORDER = (
    "package com.shop;\n\n"
    "import com.shop.Money;\n\n"
    "@Entity\n"
    "public class Order extends BaseEntity implements Serializable {\n"
    "    private String id;\n"
    "    public Money total() {\n        return null;\n    }\n"
    "}\n"
)
_MONEY = "package com.shop;\n\npublic class Money {\n}\n"


def _catalog(tmp: Path) -> object:
    (tmp / "Order.java").write_text(_ORDER)
    (tmp / "Money.java").write_text(_MONEY)
    return JavaClassCatalogExtractor().extract(tmp)


def _order(tmp: Path) -> object:
    return next(r for r in _catalog(tmp).classes if r.fqn == "com.shop.Order")  # type: ignore[attr-defined]


def test_fqn_uses_the_package(tmp_path: Path) -> None:
    assert _order(tmp_path).fqn == "com.shop.Order"  # type: ignore[attr-defined]


def test_extends_and_implements_become_bases(tmp_path: Path) -> None:
    assert _order(tmp_path).bases == ("BaseEntity", "Serializable")  # type: ignore[attr-defined]


def test_public_method_and_field_and_annotation(tmp_path: Path) -> None:
    order = _order(tmp_path)
    assert "total()" in order.methods  # type: ignore[attr-defined]
    assert "id: String" in order.fields  # type: ignore[attr-defined]
    assert "Entity" in order.decorators  # type: ignore[attr-defined]


def test_imports_resolve_to_intra_project_edges(tmp_path: Path) -> None:
    catalog = _catalog(tmp_path)
    assert catalog.import_graph["com.shop.Order"] == ("com.shop.Money",)  # type: ignore[attr-defined]


def test_test_suffixed_java_files_are_excluded(tmp_path: Path) -> None:
    (tmp_path / "OrderTest.java").write_text(
        "package com.shop;\npublic class OrderTest {}\n",
    )
    (tmp_path / "Order.java").write_text(_ORDER)
    fqns = {r.fqn for r in JavaClassCatalogExtractor().extract(tmp_path).classes}  # type: ignore[attr-defined]
    assert "com.shop.OrderTest" not in fqns
    assert "com.shop.Order" in fqns
