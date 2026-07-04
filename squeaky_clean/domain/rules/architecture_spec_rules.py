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
    for module in spec.modules:
        out.extend(_validate_module(module, all_classes, all_exports))
    return out


def _validate_module(
    module: ModuleSpec, all_classes: set[str], all_exports: set[str],
) -> list[str]:
    out: list[str] = []
    if not module.name:
        out.append("module name is empty")
    if not module.classes:
        out.append(f"module {module.name!r} declares zero classes")
    local = {c.name for c in module.classes}
    for cls in module.classes:
        for dep in cls.depends:
            bare = dep.split("::", 1)[1] if "::" in dep else dep
            if not (bare in local or (bare in all_exports and bare in all_classes)):
                out.append(f"{cls.name} depends on unknown class {dep}")
        for entry in cls.fields:
            if ":" not in entry:
                out.append(f"{cls.name} field {entry!r} missing 'name: Type'")
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
