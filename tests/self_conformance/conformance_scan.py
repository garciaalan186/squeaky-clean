"""Scan squeaky_clean/** for self-conformance violations (R2.2).

The framework's Prime Directive: its own source must obey the rules it enforces
on generated projects. This module runs the granularity rule and a
package-aware layer check over ``squeaky_clean/**`` and returns a set of
NORMALIZED violation keys.

Keys have their integers replaced with ``#`` so the ratchet allows a violation
to shrink (657→600 lines is the same key) while a genuinely new violation
(a fresh over-long file, a new upward import) surfaces as a new key.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

from squeaky_clean.domain.rules.component_dependency_rule import ComponentDependencyRule
from squeaky_clean.domain.rules.package_cohesion_rule import PackageCohesionRule
from squeaky_clean.domain.rules.python_granularity_rule import PythonGranularityRule
from squeaky_clean.domain.value_objects.violation import Violation

_PACKAGE = "squeaky_clean"
# R6.3 tranche 5: ban f-string-driven reflection (setattr/getattr with a
# dynamically built attribute name) anywhere in the framework source.
_REFLECTION_RE = re.compile(r"""(set|get)attr\([^)]*f["']""")
_LAYER_ORDER: dict[str, int] = {
    "domain": 0, "application": 1, "infrastructure": 2, "interface": 3,
}


def package_root() -> Path:
    """Absolute path to the ``squeaky_clean`` package directory."""
    return Path(__file__).resolve().parents[2] / _PACKAGE


def _iter_py_files(root: Path) -> list[Path]:
    return sorted(
        p for p in root.rglob("*.py")
        if "__pycache__" not in p.parts
    )


def _own_layer(rel_parts: tuple[str, ...]) -> str | None:
    for part in rel_parts:
        if part in _LAYER_ORDER:
            return part
    return None


def _layer_violations(path: Path, root: Path) -> list[Violation]:
    """Flag imports from an outer layer within a ``squeaky_clean.<layer>`` file."""
    rel = path.relative_to(root.parent)
    own = _own_layer(rel.parts)
    if own is None:
        return []
    try:
        tree = ast.parse(path.read_text())
    except (SyntaxError, OSError):
        return []
    own_idx = _LAYER_ORDER[own]
    out: list[Violation] = []
    seen: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom) or not node.module:
            continue
        parts = node.module.split(".")
        if len(parts) >= 2 and parts[0] == _PACKAGE and parts[1] in _LAYER_ORDER:
            target = parts[1]
            if _LAYER_ORDER[target] > own_idx and target not in seen:
                seen.add(target)
                out.append(Violation(
                    rule_name="LayerDependency",
                    file_path=str(rel),
                    message=f"{own}/ imports from {target}/ (outer layer)",
                ))
    return out


def _key(v: Violation, root: Path) -> str:
    """Normalized, integer-free key identifying one violation site."""
    p = Path(v.file_path)
    if p.is_absolute():
        try:
            rel = str(p.relative_to(root.parent))
        except ValueError:
            rel = v.file_path
    else:
        rel = v.file_path
    message = re.sub(r"\d+", "#", v.message)
    return f"{v.rule_name}|{rel}|{message}"


def _missing_mirror_keys(root: Path) -> set[str]:
    """Keys for source modules lacking a mirror ``test_<name>.py`` (R2.6).

    Basename match (a test named ``test_<name>.py`` anywhere under ``tests/``)
    keeps the check robust to test-tree reorganisation. Ratcheted like the rest:
    the current 195-module gap is the floor, and no NEW untested module may be
    added — coverage can only improve.
    """
    tests_root = root.parent / "tests"
    have = {p.name for p in tests_root.rglob("test_*.py")}
    keys: set[str] = set()
    for path in _iter_py_files(root):
        if path.name == "__init__.py":
            continue
        stem = path.stem
        # A module is covered by test_<stem>.py OR any test_<stem>_*.py
        # (modules often split coverage across _cache/_timeout suffixes).
        covered = f"test_{stem}.py" in have or any(
            name.startswith(f"test_{stem}_") for name in have
        )
        if not covered:
            rel = path.relative_to(root.parent)
            keys.add(f"MissingMirrorTest|{rel}|no mirror test file")
    return keys


def _reflection_ban_keys(root: Path) -> set[str]:
    """Keys for files using f-string setattr/getattr reflection (R6.3 t5)."""
    keys: set[str] = set()
    for path in _iter_py_files(root):
        try:
            text = path.read_text()
        except OSError:
            continue
        if _REFLECTION_RE.search(text):
            rel = path.relative_to(root.parent)
            keys.add(f"ReflectionBan|{rel}|f-string setattr/getattr")
    return keys


def scan_violation_keys() -> set[str]:
    """Return the set of normalized self-conformance violation keys."""
    root = package_root()
    granularity = PythonGranularityRule()
    keys: set[str] = set()
    for path in _iter_py_files(root):
        for v in granularity.check(path):
            keys.add(_key(v, root))
        for v in _layer_violations(path, root):
            keys.add(_key(v, root))
    for v in PackageCohesionRule().check_tree(root):
        keys.add(_key(v, root))
    for v in ComponentDependencyRule().check_tree(root):
        keys.add(_key(v, root))
    keys |= _missing_mirror_keys(root)
    keys |= _reflection_ban_keys(root)
    return keys
