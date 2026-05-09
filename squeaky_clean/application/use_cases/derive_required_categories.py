"""derive_required_categories: walk an ArchitectureSpec; pick categories."""

from __future__ import annotations

from squeaky_clean.application.use_cases.infrastructure_category_inference import (
    infer_category,
)
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType


def derive_required_categories(arch: ArchitectureSpec) -> frozenset[str]:
    """Return the set of infrastructure categories implied by the spec."""
    out: set[str] = set()
    for module in arch.modules:
        if module.layer is not LayerType.INFRASTRUCTURE:
            continue
        for cls in module.classes:
            cat = _classify(cls)
            if cat is not None:
                out.add(cat)
    return frozenset(out)


def _classify(cls: ClassSpec) -> str | None:
    method_names = tuple(_method_name(m) for m in cls.methods)
    return infer_category(method_names)


def _method_name(method_str: str) -> str:
    paren = method_str.find("(")
    return method_str[:paren] if paren > 0 else method_str
