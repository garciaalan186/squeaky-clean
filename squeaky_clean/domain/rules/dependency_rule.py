"""DependencyRule: enforces Clean Architecture inter-layer import direction."""

import ast
from pathlib import Path

from squeaky_clean.application.dtos.violation import Violation
from squeaky_clean.domain.interfaces.rule import Rule

_LAYER_ORDER: dict[str, int] = {
    "domain": 0,
    "application": 1,
    "infrastructure": 2,
    "interface": 3,
}


class DependencyRule(Rule):
    """Validates that inner layers do not import outer layers.

    A Python file at ``src/<layer>/...`` violates the rule when it
    imports from ``src.<outer_layer>.*`` where ``outer_layer`` is at a
    higher index in ``_LAYER_ORDER`` than its own layer. Files outside
    a layered ``src/`` tree are skipped (no layer to police).
    """

    _NAME = "DependencyRule"

    def check(self, path: Path) -> list[Violation]:
        """Inspect one .py file and return any cross-layer import violations."""
        if path.suffix != ".py":
            return []
        own_layer = self._own_layer(path)
        if own_layer is None:
            return []
        try:
            tree = ast.parse(path.read_text())
        except (SyntaxError, OSError):
            return []
        return self._check_imports(tree, path, own_layer)

    def _own_layer(self, path: Path) -> str | None:
        for part in path.parts:
            if part in _LAYER_ORDER:
                return part
        return None

    def _check_imports(
        self, tree: ast.Module, path: Path, own: str,
    ) -> list[Violation]:
        out: list[Violation] = []
        own_idx = _LAYER_ORDER[own]
        for node in ast.walk(tree):
            target = self._import_layer(node)
            if target is None:
                continue
            if _LAYER_ORDER[target] > own_idx:
                out.append(self._violation(path, own, target))
        return out

    def _import_layer(self, node: ast.AST) -> str | None:
        if isinstance(node, ast.ImportFrom) and node.module:
            parts = node.module.split(".")
            if len(parts) >= 2 and parts[0] == "src" and parts[1] in _LAYER_ORDER:
                return parts[1]
        return None

    def _violation(self, path: Path, own: str, target: str) -> Violation:
        return Violation(
            rule_name=self._NAME,
            file_path=str(path),
            message=f"{own}/ file imports from {target}/ (outer layer)",
        )
