"""ModelRouter: maps a ModelTier to a concrete model identifier string."""

from squeaky_clean.domain.interfaces.model_routing_policy import ModelRoutingPolicy
from squeaky_clean.domain.value_objects.model_tier import ModelTier
from squeaky_clean.infrastructure.llm.model_catalog import ModelId

# Canonical tier -> model policy (full-quality default). This is the single
# source of routing truth; RouterFactory derives its cost-tuned variant from
# it rather than keeping a second table. Concrete strings come from ModelId.
DEFAULT_MAPPING: dict[ModelTier, str] = {
    ModelTier.ARCHITECT: ModelId.OPUS,
    ModelTier.MANAGER: ModelId.SONNET,
    ModelTier.ICP: ModelId.HAIKU,
    ModelTier.FIXER: ModelId.SONNET,
}
_DEFAULT_MAPPING = DEFAULT_MAPPING  # backward-compatible alias


class ModelRouter(ModelRoutingPolicy):
    """Routes a ModelTier to the configured concrete model identifier."""

    def __init__(self, mapping: dict[ModelTier, str] | None = None) -> None:
        self._mapping: dict[ModelTier, str] = dict(
            mapping if mapping is not None else _DEFAULT_MAPPING
        )

    def route(self, tier: ModelTier) -> str:
        """Return the model string configured for the given tier."""
        if tier not in self._mapping:
            raise KeyError(f"no model configured for tier {tier}")
        return self._mapping[tier]
