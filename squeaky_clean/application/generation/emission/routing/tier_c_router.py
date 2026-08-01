"""TierCRouter: verb-heuristic + declared-category Tier C ICP inference."""

from squeaky_clean.application.generation.emission.routing.tier_c_icp_table import (
    CATEGORY_TO_ICP,
    INFRA_PATTERNS,
    INTERFACE_LAYER_CATEGORIES,
)
from squeaky_clean.application.generation.techspec.infrastructure_category_inference import (
    infer_category,
)
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType


class TierCRouter:
    """Resolves the Tier C infrastructure ICP name for one class, if any.

    H5a/H5b: the verb heuristic (``infer_category``) is tried first; when
    it yields nothing, the FIRST ``register_category``-declared category
    with a Tier C ICP wins — preferring the ProblemSpec's explicit choice
    over silent verb-name guessing. Returns None outside the Tier C gate
    (non-Repository/Gateway/Adapter patterns or inner layers).
    """

    def __init__(self) -> None:
        self._declared: list[str] = []

    def register_category(self, category: str) -> None:
        """Record a declared Tier C category (ProblemSpec order preserved)."""
        if category not in self._declared:
            self._declared.append(category)

    def route(self, cls: ClassSpec, module: ModuleSpec) -> str | None:
        """Return the Tier C ICP name for ``cls``, or None to use the catalog."""
        layer = module.layer
        if (cls.pattern not in INFRA_PATTERNS
                or layer not in (LayerType.INFRASTRUCTURE, LayerType.INTERFACE)):
            return None
        category = infer_category(self._method_names(cls))
        if category and not self._layer_matches(category, layer):
            category = None
        icp = CATEGORY_TO_ICP.get(category) if category else None
        if icp is None:
            for declared in self._declared:
                if (declared in CATEGORY_TO_ICP
                        and self._layer_matches(declared, layer)):
                    return CATEGORY_TO_ICP[declared]
        return icp

    @staticmethod
    def _method_names(cls: ClassSpec) -> tuple[str, ...]:
        return tuple(m.split("(", 1)[0].strip() for m in cls.methods if m.strip())

    @staticmethod
    def _layer_matches(category: str, layer: LayerType) -> bool:
        if category in INTERFACE_LAYER_CATEGORIES:
            return layer is LayerType.INTERFACE
        return layer is LayerType.INFRASTRUCTURE
