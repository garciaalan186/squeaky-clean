"""ModelRouter: maps a ModelTier to a concrete model identifier string."""

from squeaky_clean.domain.value_objects.model_tier import ModelTier

_DEFAULT_MAPPING: dict[ModelTier, str] = {
    ModelTier.ARCHITECT: "claude-opus-4-6",
    ModelTier.MANAGER: "claude-sonnet-4-6",
    ModelTier.ICP: "claude-haiku-4-5-20251001",
    ModelTier.FIXER: "claude-sonnet-4-6",
}


class ModelRouter:
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
