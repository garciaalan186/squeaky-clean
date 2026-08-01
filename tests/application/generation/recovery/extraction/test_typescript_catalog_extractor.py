"""Tests for TypeScriptClassCatalogExtractor: *.ts-scoped ES extraction."""

from pathlib import Path

from squeaky_clean.application.generation.recovery.extraction.typescript_catalog_extractor import (
    TypeScriptClassCatalogExtractor,
)


def test_only_ts_files_are_catalogued(tmp_path: Path) -> None:
    (tmp_path / "user.ts").write_text("export class User {}\n")
    (tmp_path / "legacy.js").write_text("export class Legacy {}\n")
    catalog = TypeScriptClassCatalogExtractor().extract(tmp_path)
    assert tuple(r.fqn for r in catalog.classes) == ("user.User",)


def test_fqn_is_path_derived_and_nested_dirs_walk(tmp_path: Path) -> None:
    sub = tmp_path / "src" / "domain"
    sub.mkdir(parents=True)
    (sub / "cart.ts").write_text("export abstract class Cart extends Base {}\n")
    catalog = TypeScriptClassCatalogExtractor().extract(tmp_path)
    record = catalog.classes[0]
    assert record.fqn == "src.domain.cart.Cart"
    assert record.bases == ("Base",)


def test_members_imports_and_decorators_are_recovered(tmp_path: Path) -> None:
    (tmp_path / "user_service.ts").write_text(
        'import { Repo } from "./repo";\n'
        "\n"
        "@Injectable\n"
        "export class UserService implements OnInit {\n"
        "  private repo: Repo;\n"
        "  findUser(id: string): User {\n"
        "  }\n"
        "}\n"
    )
    (record,) = TypeScriptClassCatalogExtractor().extract(tmp_path).classes
    assert record.bases == ("OnInit",)
    assert record.methods == ("findUser(id: string)",)
    assert record.fields == ("repo: Repo",)
    assert record.imports == ("./repo",)
    assert record.decorators == ("Injectable",)
