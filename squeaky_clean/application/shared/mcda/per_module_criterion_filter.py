"""PerModuleCriterionFilter: drop criteria whose verb no class in the module owns.

The TestArchitect emits an honest pessimistic stub
(``pytest.fail("verb X not in ModuleSpec")``) for every criterion whose
verb appears in no class's ``methods:`` list. Showing all criteria to all
modules therefore produces many such stubs, dragging ``tests_pass`` down.
This filter is invoked by ``TestArchitectureContextFormatter.format`` so
each module's TestArchitect call only sees the criteria it can honestly
test.
"""

from __future__ import annotations

import re
from collections.abc import Sequence

from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType

_WHEN_RE = re.compile(r"\bWhen\s+([A-Za-z_][A-Za-z0-9_]*)", re.IGNORECASE)
_VO_PATTERNS = frozenset({"ValueObject", "Value Object"})


def _normalize(token: str) -> str:
    return token.replace("_", "").lower()


def _verb_of(criterion: str) -> str | None:
    match = _WHEN_RE.search(criterion)
    return match.group(1) if match else None


def _method_name(method_signature: str) -> str:
    head = method_signature.split("(", 1)[0].strip()
    return head


def _module_method_names(module: ModuleSpec) -> set[str]:
    names: set[str] = set()
    for cls in module.classes:
        # A verb owned only by an abstract Gateway port has no concrete,
        # unit-testable implementation here — testing it would instantiate the
        # abstract port. Leave it to the developer's integration tests.
        if cls.pattern == "Gateway":
            continue
        for method in cls.methods:
            names.add(_normalize(_method_name(method)))
    return names


def _is_value_object_only_domain(module: ModuleSpec) -> bool:
    if module.layer is not LayerType.DOMAIN:
        return False
    if not module.classes:
        return False
    return all(cls.pattern in _VO_PATTERNS for cls in module.classes)


def filter_criteria_for_module(
    criteria: Sequence[str],
    module: ModuleSpec,
) -> tuple[str, ...]:
    """Return the subset of ``criteria`` whose verb is owned by ``module``.

    A criterion without a "When <verb> is called" clause is kept (honest
    fallback unchanged). A module with zero classes, or a Domain-layer
    module containing only ValueObjects, returns an empty filter.
    """
    if not module.classes:
        return ()
    if _is_value_object_only_domain(module):
        return ()
    method_names = _module_method_names(module)
    kept: list[str] = []
    for criterion in criteria:
        verb = _verb_of(criterion)
        if verb is None:
            kept.append(criterion)
            continue
        if _normalize(verb) in method_names:
            kept.append(criterion)
    return tuple(kept)
