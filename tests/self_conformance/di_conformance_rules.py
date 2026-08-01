"""R6.4 DI-regime conformance rules: fs-port honesty + impure construction.

Two AST scanners feeding the self-conformance ratchet:

``FsPortBypass`` — raw ``.write_text(...)`` / ``.write_bytes(...)`` attribute
calls. Scope (chosen 2026-07-31, R6.4a): WRITES ONLY — ``mkdir``/``exists``/
``open`` are out of scope (survey found zero write-mode ``open()`` under
application/ and mkdir is directory bookkeeping, not artifact content).
  * under ``application/generation/**``: any raw write is a violation —
    user artifacts go through the ProjectFileSystem port.
  * under ``application/evaluation/**``: any raw write is a violation —
    framework artifacts go through ``atomic_write_text`` (calls to it are
    ordinary function calls, not attribute writes, so they pass). The
    helper itself lives in ``application/shared/io/atomic_write.py``,
    outside both scopes.

``ImpureConstruction`` — construction of a denylisted I/O-touching class
anywhere under ``application/**`` (module top level, ``__init__`` or method
bodies alike — every ``Call`` node counts). These must be injected from the
composition root (dependency_builder / interface layer).
"""

from __future__ import annotations

import ast
from pathlib import Path

_WRITE_ATTRS = frozenset({"write_text", "write_bytes"})
# Denylist (R6.4d): classes that touch fs/network/env. Full list from the
# roadmap retained — LoadAgentSpec was the only one with live offenders.
_DENYLIST = frozenset({
    "JSONLogger", "LocalFileSystem", "ClaudeCLIGateway", "AnthropicSDKGateway",
    "CachingLLMGateway", "ContentAddressedCache", "LoadAgentSpec",
})


def _parse(path: Path) -> ast.Module | None:
    try:
        return ast.parse(path.read_text())
    except (SyntaxError, OSError):
        return None


def fs_port_bypass_keys(path: Path, rel: str) -> set[str]:
    """FsPortBypass keys for one file under application/generation|evaluation."""
    posix = Path(rel).as_posix()
    in_gen = "/application/generation/" in f"/{posix}"
    in_eval = "/application/evaluation/" in f"/{posix}"
    if not (in_gen or in_eval):
        return set()
    tree = _parse(path)
    if tree is None:
        return set()
    message = (
        "raw Path write in generation/" if in_gen
        else "non-atomic write in evaluation/"
    )
    for node in ast.walk(tree):
        if (isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr in _WRITE_ATTRS):
            return {f"FsPortBypass|{rel}|{message}"}
    return set()


def impure_construction_keys(path: Path, rel: str) -> set[str]:
    """ImpureConstruction keys for one file under application/**."""
    if "/application/" not in f"/{Path(rel).as_posix()}":
        return set()
    tree = _parse(path)
    if tree is None:
        return set()
    keys: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        name = func.id if isinstance(func, ast.Name) else (
            func.attr if isinstance(func, ast.Attribute) else None
        )
        if name in _DENYLIST:
            keys.add(f"ImpureConstruction|{rel}|{name} constructed in application")
    return keys
