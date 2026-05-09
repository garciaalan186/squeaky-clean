"""TemperaturePolicy: per-tier sampling policy (temperature + seed)."""

from dataclasses import dataclass

from squeaky_clean.domain.value_objects.model_tier import ModelTier


@dataclass(frozen=True)
class TierSampling:
    """Sampling settings for one tier: temperature + optional seed."""

    temperature: float
    seed: int | None


_DEFAULT: dict[ModelTier, TierSampling] = {
    ModelTier.ARCHITECT: TierSampling(temperature=0.0, seed=0),
    ModelTier.MANAGER: TierSampling(temperature=0.0, seed=0),
    ModelTier.ICP: TierSampling(temperature=0.2, seed=0),
    ModelTier.FIXER: TierSampling(temperature=0.0, seed=0),
}


@dataclass(frozen=True)
class TemperaturePolicy:
    """Maps a ModelTier to a TierSampling. Immutable, defaults are A4 spec."""

    settings: dict[ModelTier, TierSampling]

    @classmethod
    def default(cls) -> "TemperaturePolicy":
        """Return the A4-default policy (architect/manager/fixer determinic)."""
        return cls(settings=dict(_DEFAULT))

    @classmethod
    def deterministic(cls) -> "TemperaturePolicy":
        """All tiers pinned to temperature=0, seed=0."""
        return cls(settings={
            tier: TierSampling(temperature=0.0, seed=0)
            for tier in ModelTier
        })

    def for_tier(self, tier: ModelTier) -> TierSampling:
        """Look up sampling settings for ``tier``."""
        return self.settings[tier]
