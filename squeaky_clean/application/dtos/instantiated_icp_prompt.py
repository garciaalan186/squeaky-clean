"""InstantiatedICPPrompt DTO: a fully-rendered ICP prompt ready for dispatch."""

from dataclasses import dataclass

from squeaky_clean.domain.value_objects.model_tier import ModelTier


@dataclass(frozen=True)
class InstantiatedICPPrompt:
    """Frozen output of TechSpecComposer: system + user prompt + tier (H2)."""

    system_prompt: str
    user_prompt: str
    model_tier: ModelTier
