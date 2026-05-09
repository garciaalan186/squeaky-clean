"""Tests for DependencyRule (layered import direction)."""

from pathlib import Path

from squeaky_clean.domain.rules.dependency_rule import DependencyRule


def test_dependency_rule_skips_files_outside_layered_tree(tmp_path: Path) -> None:
    f = tmp_path / "loose.py"
    f.write_text("from src.application.x import Y\n")
    rule = DependencyRule()
    assert rule.check(f) == []


def test_dependency_rule_passes_clean_inner_layer(tmp_path: Path) -> None:
    f = tmp_path / "src" / "domain" / "auth" / "user.py"
    f.parent.mkdir(parents=True)
    f.write_text("class User:\n    pass\n")
    assert DependencyRule().check(f) == []


def test_dependency_rule_allows_inner_to_inner_imports(tmp_path: Path) -> None:
    f = tmp_path / "src" / "application" / "auth" / "service.py"
    f.parent.mkdir(parents=True)
    f.write_text("from src.domain.auth.user import User\n")
    assert DependencyRule().check(f) == []


def test_dependency_rule_flags_domain_importing_application(tmp_path: Path) -> None:
    f = tmp_path / "src" / "domain" / "auth" / "user.py"
    f.parent.mkdir(parents=True)
    f.write_text("from src.application.auth.service import Service\n")
    out = DependencyRule().check(f)
    assert len(out) == 1
    assert "domain/" in out[0].message
    assert "application/" in out[0].message


def test_dependency_rule_flags_application_importing_infrastructure(
    tmp_path: Path,
) -> None:
    f = tmp_path / "src" / "application" / "auth" / "service.py"
    f.parent.mkdir(parents=True)
    f.write_text("from src.infrastructure.db.repo import Repo\n")
    out = DependencyRule().check(f)
    assert len(out) == 1


def test_dependency_rule_skips_non_python(tmp_path: Path) -> None:
    f = tmp_path / "src" / "domain" / "x.txt"
    f.parent.mkdir(parents=True)
    f.write_text("anything")
    assert DependencyRule().check(f) == []
