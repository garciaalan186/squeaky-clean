"""TierSampling: sampling settings for one tier (temperature + seed)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class TierSampling:
    """Sampling settings for one tier: temperature + optional seed."""

    temperature: float
    seed: int | None
