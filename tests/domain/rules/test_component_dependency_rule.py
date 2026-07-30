"""Tests for ComponentDependencyRule."""

from pathlib import Path

from squeaky_clean.domain.rules.component_dependency_rule import ComponentDependencyRule


def _mod(root: Path, component: str, name: str, imports: str) -> None:
    d = root / "squeaky_clean" / "application" / component
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{name}.py").write_text(imports + "\n")


def _check(root: Path) -> list[str]:
    viols = ComponentDependencyRule().check_tree(root / "squeaky_clean")
    return [v.message for v in viols]


def test_generation_importing_evaluation_is_forbidden(tmp_path: Path) -> None:
    _mod(tmp_path, "generation", "a",
         "from squeaky_clean.application.evaluation.eval.x import Y")
    assert any("generation/ imports evaluation/" in m for m in _check(tmp_path))


def test_shared_importing_generation_is_forbidden(tmp_path: Path) -> None:
    _mod(tmp_path, "shared", "a",
         "from squeaky_clean.application.generation.emission.x import Y")
    assert any("shared/ imports generation/" in m for m in _check(tmp_path))


def test_evaluation_importing_generation_is_allowed(tmp_path: Path) -> None:
    _mod(tmp_path, "evaluation", "a",
         "from squeaky_clean.application.generation.emission.x import Y")
    assert _check(tmp_path) == []


def test_intra_component_import_is_allowed(tmp_path: Path) -> None:
    _mod(tmp_path, "generation", "a",
         "from squeaky_clean.application.generation.notation.x import Y")
    assert _check(tmp_path) == []
