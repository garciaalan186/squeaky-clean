"""Foreign-import policing for pure layers (domain/application).

Layers that must stay free of concrete third-party clients/SDKs: the
Dependency Rule says Domain imports nothing outward and Application
only Domain. A bounded allowlist (the language standard library) is
permitted; everything else non-first-party is a foreign coupling.

Pure functions used by ``DependencyRule``; violations surface under the
parent rule's name so report consumers see one rule for one principle.
"""

import ast
import sys
from pathlib import Path

from squeaky_clean.domain.value_objects.violation import Violation

_RULE_NAME = "DependencyRule"
_PURE_LAYERS: frozenset[str] = frozenset({"domain", "application"})
_STDLIB: frozenset[str] = frozenset(sys.stdlib_module_names)


def polices_foreign(own: str, path: Path) -> bool:
    """True when ``path`` is production source in a pure layer.

    The no-third-party rule governs domain/application *source*; test
    modules legitimately import test frameworks (pytest, mocks), so
    anything under ``tests/`` or named ``test_*`` is exempt.
    """
    if own not in _PURE_LAYERS:
        return False
    if "tests" in path.parts or path.name.startswith("test_"):
        return False
    return "src" in path.parts


def foreign_violations(node: ast.AST, path: Path, own: str) -> list[Violation]:
    """Flag concrete third-party imports inside a pure (domain/app) file."""
    for top in _imported_tops(node):
        if top and top != "src" and top not in _STDLIB:
            return [Violation(
                rule_name=_RULE_NAME,
                file_path=str(path),
                message=(f"{own}/ file imports third-party module "
                         f"'{top}' (only stdlib + first-party allowed)"),
            )]
    return []


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
