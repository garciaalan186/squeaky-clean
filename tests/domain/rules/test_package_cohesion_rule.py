"""Tests for PackageCohesionRule."""

from pathlib import Path

from squeaky_clean.domain.rules.package_cohesion_rule import PackageCohesionRule


def _pkg(root: Path, name: str, n_modules: int) -> None:
    d = root / "squeaky_clean" / name
    d.mkdir(parents=True)
    (d / "__init__.py").write_text("")
    for i in range(n_modules):
        (d / f"mod_{i}.py").write_text("x = 1\n")


def test_oversized_package_flagged(tmp_path: Path) -> None:
    _pkg(tmp_path, "big", 21)
    viols = PackageCohesionRule().check_tree(tmp_path / "squeaky_clean")
    assert any("21 modules (>20)" in v.message for v in viols)


def test_package_at_cap_is_clean(tmp_path: Path) -> None:
    _pkg(tmp_path, "ok", 20)
    viols = PackageCohesionRule().check_tree(tmp_path / "squeaky_clean")
    assert [v for v in viols if v.file_path.endswith("ok")] == []


def test_catchall_name_flagged(tmp_path: Path) -> None:
    _pkg(tmp_path, "use_cases", 2)
    viols = PackageCohesionRule().check_tree(tmp_path / "squeaky_clean")
    assert any("catch-all" in v.message for v in viols)
