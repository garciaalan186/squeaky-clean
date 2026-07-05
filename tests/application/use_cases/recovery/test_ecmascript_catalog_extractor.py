"""Tests for the JavaScript/TypeScript catalog extractors."""

from pathlib import Path

from squeaky_clean.application.dtos.recovery.class_record import ClassRecord
from squeaky_clean.application.use_cases.recovery.javascript_catalog_extractor import (
    JavaScriptClassCatalogExtractor,
)
from squeaky_clean.application.use_cases.recovery.typescript_catalog_extractor import (
    TypeScriptClassCatalogExtractor,
)

_TS = (
    "import { Widget } from './widget';\n\n"
    "@Controller\n"
    "export class PageController extends Base implements Handler {\n"
    "    title: string;\n"
    "    render(id: string): string {\n        return '';\n    }\n"
    "}\n"
)
_JS = (
    "export class Cart {\n"
    "    add(item) {\n        this.items.push(item);\n    }\n"
    "}\n"
)


def _only(records: tuple[ClassRecord, ...], fqn_end: str) -> ClassRecord:
    return next(r for r in records if r.fqn.endswith(fqn_end))


def test_typescript_class_is_extracted(tmp_path: Path) -> None:
    (tmp_path / "page.ts").write_text(_TS)
    rec = _only(TypeScriptClassCatalogExtractor().extract(tmp_path).classes, ".PageController")
    assert rec.fqn == "page.PageController"
    assert rec.bases == ("Base", "Handler")
    assert "render(id: string)" in rec.methods
    assert "title: string" in rec.fields
    assert "Controller" in rec.decorators


def test_javascript_class_and_method(tmp_path: Path) -> None:
    (tmp_path / "cart.js").write_text(_JS)
    rec = _only(JavaScriptClassCatalogExtractor().extract(tmp_path).classes, ".Cart")
    assert rec.fqn == "cart.Cart"
    assert rec.methods == ("add(item)",)


def test_test_and_spec_files_are_excluded(tmp_path: Path) -> None:
    (tmp_path / "page.ts").write_text(_TS)
    (tmp_path / "page.spec.ts").write_text("export class Spec {}\n")
    (tmp_path / "page.test.ts").write_text("export class T {}\n")
    fqns = {r.fqn for r in TypeScriptClassCatalogExtractor().extract(tmp_path).classes}
    assert fqns == {"page.PageController"}
