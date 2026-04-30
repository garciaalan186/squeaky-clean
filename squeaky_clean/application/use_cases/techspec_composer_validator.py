"""Pure-function validator for TechSpec/ClassSpec coherence (H2)."""

from __future__ import annotations

import re
from typing import cast

from squeaky_clean.application.dtos.tech_spec import TechSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec

_GENERIC_VERBS: frozenset[str] = frozenset({
    "save", "put", "get", "delete", "find", "publish",
    "consume", "set", "expire", "invoke",
})
_ENV_VAR = re.compile(r"^[A-Z][A-Z0-9_]+$")


def _method_name(method_decl: str) -> str:
    return method_decl.split("(", 1)[0].strip()


def _is_generic_verb(name: str) -> bool:
    head = name.split("_", 1)[0].lower()
    return head in _GENERIC_VERBS


def _imported_types(spec: TechSpec) -> set[str]:
    types_obj = cast(list[object], spec.imports.get("types") or [])
    out: set[str] = set()
    for line in types_obj:
        s = str(line)
        if " import " in s:
            tail = s.split(" import ", 1)[1]
            for tok in tail.replace(",", " ").split():
                if tok.isidentifier():
                    out.add(tok)
    return out


def _allowed_deps(class_spec: ClassSpec, tech_spec: TechSpec) -> set[str]:
    out: set[str] = set(_imported_types(tech_spec))
    if class_spec.implements:
        out.add(class_spec.implements)
    return out


def validate_composition(
    class_spec: ClassSpec, tech_spec: TechSpec,
    sibling_names: frozenset[str] = frozenset(),
) -> tuple[str, ...]:
    """Return validation errors as a tuple. Empty tuple = clean composition."""
    errors: list[str] = []
    op_names = {op.name for op in tech_spec.primary_operations}
    for method in class_spec.methods:
        name = _method_name(method)
        if _is_generic_verb(name) and name not in op_names:
            errors.append(
                f"method {name!r} is not in TechSpec.primary_operations"
            )
    allowed = _allowed_deps(class_spec, tech_spec) | sibling_names
    for dep in class_spec.depends:
        if dep not in allowed:
            errors.append(
                f"dependency {dep!r} is neither a sibling nor TechSpec import"
            )
    env_vars = cast(list[object], tech_spec.auth.get("env_vars") or [])
    for var in env_vars:
        if not _ENV_VAR.match(str(var)):
            errors.append(f"auth.env_vars entry {var!r} is not a valid identifier")
    return tuple(errors)
