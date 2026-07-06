"""DependencyRule: enforces Clean Architecture inter-layer import direction."""

import ast
import sys
from pathlib import Path

from squeaky_clean.application.dtos.violation import Violation
from squeaky_clean.domain.interfaces.rule import Rule

_LAYER_ORDER: dict[str, int] = {
    "domain": 0,
    "application": 1,
    "infrastructure": 2,
    "interface": 3,
}

# Layers that must stay free of concrete third-party clients/SDKs: the
# Dependency Rule says Domain imports nothing outward and Application
# only Domain. A bounded allowlist (the language standard library) is
# permitted; everything else non-first-party is a foreign coupling.
_PURE_LAYERS: frozenset[str] = frozenset({"domain", "application"})
_STDLIB: frozenset[str] = frozenset(sys.stdlib_module_names)


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
        police_foreign = own in _PURE_LAYERS and self._is_production(path)
        for node in ast.walk(tree):
            target = self._import_layer(node)
            if target is not None and _LAYER_ORDER[target] > own_idx:
                out.append(self._violation(path, own, target))
            if police_foreign:
                out.extend(self._foreign(node, path, own))
        return out

    @staticmethod
    def _is_production(path: Path) -> bool:
        """True for a production ``src/`` file (test code may import freely).

        The no-third-party rule governs domain/application *source*; test
        modules legitimately import test frameworks (pytest, mocks), so
        anything under ``tests/`` or named ``test_*`` is exempt.
        """
        if "tests" in path.parts or path.name.startswith("test_"):
            return False
        return "src" in path.parts

    def _foreign(
        self, node: ast.AST, path: Path, own: str,
    ) -> list[Violation]:
        """Flag concrete third-party imports inside a pure (domain/app) file."""
        for top in self._imported_tops(node):
            if top and top != "src" and top not in _STDLIB:
                return [Violation(
                    rule_name=self._NAME,
                    file_path=str(path),
                    message=(f"{own}/ file imports third-party module "
                             f"'{top}' (only stdlib + first-party allowed)"),
                )]
        return []

    @staticmethod
    def _imported_tops(node: ast.AST) -> list[str]:
        """Top-level module name(s) of an import, or [] for non-imports.

        Relative imports (``from . import x``) are first-party and yield
        no name to police.
        """
        if isinstance(node, ast.Import):
            return [alias.name.split(".")[0] for alias in node.names]
        if isinstance(node, ast.ImportFrom):
            if node.level and node.level > 0:
                return []
            return [node.module.split(".")[0]] if node.module else []
        return []

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
