"""ComponentDependencyRule: ADP/SDP across application components (R1.7)."""

import ast
from pathlib import Path

from squeaky_clean.domain.value_objects.violation import Violation

# Allowed dependency targets per application component (the component DAG).
_ALLOWED: dict[str, frozenset[str]] = {
    "generation": frozenset({"shared"}),
    "evaluation": frozenset({"generation", "shared"}),
    "shared": frozenset(),
}
_COMPONENTS = frozenset(_ALLOWED)


class ComponentDependencyRule:
    """Enforces the application component DAG (generation/evaluation/shared).

    ``generation -> shared``; ``evaluation -> {generation, shared}``; ``shared``
    depends on nothing but ``domain``. Forbids ``generation -> evaluation`` (the
    product must never import its eval harness) and any ``shared -> {generation,
    evaluation}``, plus any cycle.
    """

    _NAME = "ComponentDependencyRule"

    def check_tree(self, root: Path) -> list[Violation]:
        """Return component-boundary violations under ``root/application``."""
        app = root / "application"
        out: list[Violation] = []
        for path in sorted(app.rglob("*.py")):
            if "__pycache__" not in path.parts:
                out.extend(self._check_file(path, root))
        return out

    def _check_file(self, path: Path, root: Path) -> list[Violation]:
        own = self._component(path.relative_to(root / "application"))
        if own is None:
            return []
        rel = str(path.relative_to(root.parent))
        return [
            Violation(self._NAME, rel, f"{own}/ imports {tgt}/ (component DAG)")
            for tgt in sorted(self._targets(path))
            if tgt != own and tgt not in _ALLOWED[own]
        ]

    @staticmethod
    def _component(rel: Path) -> str | None:
        top = rel.parts[0] if rel.parts else ""
        return top if top in _COMPONENTS else None

    @staticmethod
    def _targets(path: Path) -> set[str]:
        try:
            tree = ast.parse(path.read_text())
        except (SyntaxError, OSError):
            return set()
        out: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                p = node.module.split(".")
                if p[:2] == ["squeaky_clean", "application"] and len(p) >= 3:
                    if p[2] in _COMPONENTS:
                        out.add(p[2])
        return out
