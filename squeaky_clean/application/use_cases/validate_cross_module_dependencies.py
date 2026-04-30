"""validate_cross_module_dependencies: cross-module dep validator.

Pure function over an in-memory ``ArchitectureSpec``. Returns one
human-readable violation string per offending ``depends`` entry.

Complementary to ``ArchitectureSpec.validate()`` — that helper accepts a
cross-module class if *any* module exports it, but does NOT enforce that
the target module is the correct one, that the importing module declares
the target in its top-level ``DEPENDS``, or that the target module
actually declares the class. This validator covers exactly those gaps.
"""

from __future__ import annotations

from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec


def validate_cross_module_dependencies(
    arch: ArchitectureSpec,
) -> tuple[str, ...]:
    """Return tuple of cross-module dependency violation strings."""
    by_name: dict[str, ModuleSpec] = {m.name: m for m in arch.modules}
    all_exports: set[str] = {e for m in arch.modules for e in m.exports}
    all_classes: set[str] = {c.name for m in arch.modules for c in m.classes}
    out: list[str] = []
    for module in arch.modules:
        local = {c.name for c in module.classes}
        for cls in module.classes:
            for dep in cls.depends:
                msg = _check_dep(
                    module, cls.name, dep, by_name, local,
                    all_exports, all_classes,
                )
                if msg is not None:
                    out.append(msg)
    return tuple(out)


def _check_dep(
    module: ModuleSpec,
    cls_name: str,
    dep: str,
    by_name: dict[str, ModuleSpec],
    local: set[str],
    all_exports: set[str],
    all_classes: set[str],
) -> str | None:
    """Return a violation string for one ``depends`` entry, or None.

    Bare (unqualified) deps fall back to the legacy leniency in
    ``ArchitectureSpec.validate()`` — accepted if the name is local
    or exported by some module — to preserve compatibility with the
    architect's current convention. Qualified ``Module::Type`` deps
    are checked strictly per C4.
    """
    prefix = f"module {module.name!r} class {cls_name!r} dep {dep!r}"
    if "::" not in dep:
        if dep in local or (dep in all_exports and dep in all_classes):
            return None
        return f"{prefix}: unknown intra-module class"
    target_name, _, type_name = dep.partition("::")
    if target_name == module.name:
        if type_name in local:
            return None
        return f"{prefix}: self-reference to undeclared class"
    target = by_name.get(target_name)
    if target is None:
        return f"{prefix}: unknown module {target_name!r}"
    if target_name not in module.depends:
        return (f"{prefix}: target module {target_name!r} not in "
                f"importing module's DEPENDS list")
    if type_name not in {c.name for c in target.classes}:
        return f"{prefix}: type {type_name!r} not declared in {target_name!r}"
    if type_name not in target.exports:
        return f"{prefix}: type {type_name!r} not in {target_name!r}.EXPORTS"
    return None
