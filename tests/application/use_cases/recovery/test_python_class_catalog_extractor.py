"""Tests for PythonClassCatalogExtractor (Stage-1 brownfield ingest)."""

from pathlib import Path

from squeaky_clean.application.use_cases.recovery.python_class_catalog_extractor import (
    PythonClassCatalogExtractor,
)

_USER = '''\
from dataclasses import dataclass


@dataclass
class User:
    id: str
    name: str

    def rename(self, name: str) -> None:
        self._name = name

    def _private(self) -> None:
        pass
'''

_SERVICE = '''\
from shop.domain.user import User


class UserService:
    def register(self, user: User) -> None:
        self.last = user
'''


def _tree(tmp: Path) -> Path:
    root = tmp / "shop"
    (root / "domain").mkdir(parents=True, exist_ok=True)
    (root / "__init__.py").write_text("")
    (root / "domain" / "__init__.py").write_text("")
    (root / "domain" / "user.py").write_text(_USER)
    (root / "domain" / "user_service.py").write_text(_SERVICE)
    return tmp


def _by_fqn(tmp: Path) -> dict[str, object]:
    catalog = PythonClassCatalogExtractor().extract(_tree(tmp))
    return {r.fqn: r for r in catalog.classes}


def test_discovers_all_classes_with_fqns(tmp_path: Path) -> None:
    records = _by_fqn(tmp_path)
    assert set(records) == {
        "shop.domain.user.User",
        "shop.domain.user_service.UserService",
    }


def test_public_methods_drop_self_and_underscore(tmp_path: Path) -> None:
    user = _by_fqn(tmp_path)["shop.domain.user.User"]
    assert user.methods == ("rename(name)",)  # type: ignore[attr-defined]


def test_captures_fields_bases_and_decorators(tmp_path: Path) -> None:
    user = _by_fqn(tmp_path)["shop.domain.user.User"]
    assert user.decorators == ("dataclass",)  # type: ignore[attr-defined]
    assert "id: str" in user.fields  # type: ignore[attr-defined]
    assert "_name" in user.fields  # type: ignore[attr-defined]


def test_import_graph_resolves_sibling_edges_only(tmp_path: Path) -> None:
    catalog = PythonClassCatalogExtractor().extract(_tree(tmp_path))
    graph = catalog.import_graph
    svc = "shop.domain.user_service.UserService"
    assert graph[svc] == ("shop.domain.user.User",)
    assert graph["shop.domain.user.User"] == ()


def test_unparseable_file_is_skipped(tmp_path: Path) -> None:
    tree = _tree(tmp_path)
    (tree / "shop" / "broken.py").write_text("def (:\n")
    records = _by_fqn(tmp_path)
    assert "shop.domain.user.User" in records
