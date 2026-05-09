"""PortMethodDecomposer: split >3-method Tier C ClassSpecs into Facade+siblings.

Pure mechanical transformation applied BEFORE pattern assignment, so the
EM only sees ≤3-method classes. Tier C / infrastructure routing only.

Naming: focal `FooConsumer` with methods `[a, b, c, d]` becomes
`FooConsumerAB` + `FooConsumerCD` collaborators plus a `FooConsumer`
Facade. Suffixes are concatenated UpperCamel initials of the methods.
"""

from __future__ import annotations

from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec


def _suffix(methods: tuple[str, ...]) -> str:
    parts: list[str] = []
    for m in methods:
        head = m.split("(", 1)[0].strip().lstrip("_")
        if head:
            parts.append("".join(
                p[:1].upper() + p[1:] for p in head.split("_") if p
            ))
    return "".join(parts) or "Group"


def _split_groups(methods: tuple[str, ...]) -> tuple[tuple[str, ...], ...]:
    n = len(methods)
    if n <= 3:
        return (methods,)
    if n == 4:
        return (methods[:2], methods[2:])
    if n in (5, 6):
        return (methods[:3], methods[3:])
    return (methods[:3], methods[3:6], methods[6:])


def _collaborator(focal: ClassSpec, group: tuple[str, ...]) -> ClassSpec:
    return ClassSpec(
        name=f"{focal.name}{_suffix(group)}", pattern=focal.pattern,
        implements=None, methods=group, depends=focal.depends, concretes=(),
        fields=focal.fields, invariants=focal.invariants,
    )


def decompose_class(focal: ClassSpec) -> tuple[ClassSpec, ...]:
    """Return (focal,) when ≤3 methods; otherwise (collaborators..., facade)."""
    if len(focal.methods) <= 3:
        return (focal,)
    sibs = tuple(_collaborator(focal, g) for g in _split_groups(focal.methods))
    facade = ClassSpec(
        name=focal.name, pattern="Facade", implements=focal.implements,
        methods=focal.methods, depends=tuple(s.name for s in sibs),
        concretes=(), fields=focal.fields, invariants=focal.invariants,
    )
    return (*sibs, facade)


def decompose_module_for_tier_c(
    module: ModuleSpec, tier_c_class_names: frozenset[str],
) -> ModuleSpec:
    """Replace each Tier C class in `module` by its decomposition."""
    if not tier_c_class_names:
        return module
    new_classes: list[ClassSpec] = []
    for c in module.classes:
        if c.name in tier_c_class_names and len(c.methods) > 3:
            new_classes.extend(decompose_class(c))
        else:
            new_classes.append(c)
    return ModuleSpec(
        name=module.name, layer=module.layer, exports=module.exports,
        depends=module.depends, classes=tuple(new_classes),
        invariants=module.invariants,
    )
