"""RouterFactory: build a ModelRouter from optional CLI override arguments."""

from squeaky_clean.domain.value_objects.model_tier import ModelTier
from squeaky_clean.infrastructure.llm.model_router import ModelRouter

_PHASE5_MAPPING: dict[ModelTier, str] = {
    ModelTier.ARCHITECT: "claude-sonnet-4-6",
    ModelTier.MANAGER: "claude-sonnet-4-6",
    ModelTier.ICP: "claude-haiku-4-5-20251001",
    ModelTier.FIXER: "claude-sonnet-4-6",
}


class RouterFactory:
    """Constructs a ModelRouter using Phase-5 defaults or a forced override.

    Phase-5 default demotes ARCHITECT from Opus to Sonnet for cost
    control. Phase 6 is expected to re-enable Opus after prompt
    iteration is stable and we can afford A/B comparison runs.
    """

    def build(self, override: str | None) -> ModelRouter:
        """Return a ModelRouter — forced to ``override`` if set."""
        if override is None:
            return ModelRouter(dict(_PHASE5_MAPPING))
        mapping: dict[ModelTier, str] = {tier: override for tier in ModelTier}
        return ModelRouter(mapping)
