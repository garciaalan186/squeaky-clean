"""ArchitectureSpec validation rules: pure functions over the parsed spec.

Catches cycles, unknown deps, empty modules, malformed fields, and
class-shape violations (rule 4 >5 methods; rule 13 decorative empty
classes) BEFORE any ICP fires.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
    from squeaky_clean.domain.entities.class_spec import ClassSpec
    from squeaky_clean.domain.entities.module_spec import ModuleSpec

_SPEC_MAX_METHODS = 5


def collect_violations(spec: ArchitectureSpec) -> list[str]:
    """Return all spec-level violations as flat strings."""
    out: list[str] = []
    if not spec.modules:
        out.append("no modules declared")
    names = {m.name for m in spec.modules}
    all_classes = {c.name for m in spec.modules for c in m.classes}
    all_exports = {e for m in spec.modules for e in m.exports}
    for src, deps in spec.graph.edges.items():
        if src not in names:
            out.append(f"graph edge from unknown module {src!r}")
        for dep in deps:
            if dep not in names:
                out.append(f"module {src!r} depends on unknown module {dep!r}")
    out.extend(f"cycle: {c}" for c in spec.graph.cycle_violations())
    # Cross-module leniency: a bare dep resolves if some module both
    # exports AND declares it (strict per-edge checks are R6.6c's
    # cross_module_dependency_rules, surfaced separately).
    external = all_exports & all_classes
    for module in spec.modules:
        out.extend(_validate_module(module, external))
    return out


def _validate_module(module: ModuleSpec, external: set[str]) -> list[str]:
    out: list[str] = []
    if not module.name:
        out.append("module name is empty")
    if not module.classes:
        out.append(f"module {module.name!r} declares zero classes")
    # Unknown-dep and field-syntax invariants live ONCE on the entities
    # (ModuleSpec/ClassSpec, R6.6c); this rule module only orchestrates.
    out.extend(module.unknown_dep_violations(external))
    out.extend(module.field_syntax_violations())
    for cls in module.classes:
        out.extend(_validate_class_shape(cls))
    return out


def _validate_class_shape(cls: ClassSpec) -> list[str]:
    """Enforce PrincipalArchitect rules 4 (≤5 methods) and 13 (no decorative classes)."""
    out: list[str] = []
    if len(cls.methods) > _SPEC_MAX_METHODS:
        out.append(
            f"{cls.name} declares {len(cls.methods)} methods "
            f"(>{_SPEC_MAX_METHODS}); decompose via Strategy or Facade"
        )
    if not cls.methods and not cls.invariants:
        out.append(
            f"{cls.name} has no methods and no invariants; "
            f"forbidden by rule 13 (minimal type decomposition) — "
            f"delete the class and use the underlying primitive"
        )
    return out
