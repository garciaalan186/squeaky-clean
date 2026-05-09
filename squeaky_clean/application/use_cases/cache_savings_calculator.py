"""CacheSavingsCalculator: derive hit ratios and USD savings from token totals."""

from __future__ import annotations

from dataclasses import dataclass

from squeaky_clean.infrastructure.llm.model_pricing import estimate_cost_usd

_CACHE_READ_DISCOUNT: float = 0.9
_CACHE_CREATE_PREMIUM: float = 0.25


@dataclass(frozen=True)
class TierCacheTokens:
    """Cache create/read totals plus the model used for one tier."""

    create_tokens: int
    read_tokens: int
    model: str


class CacheSavingsCalculator:
    """Compute (hit_ratio, savings_usd) from per-tier cache token totals."""

    def hit_ratio(self, tier: TierCacheTokens) -> float:
        """Return cache_read / (read + create); 0.0 when no cache activity."""
        denom = tier.create_tokens + tier.read_tokens
        if denom <= 0:
            return 0.0
        return tier.read_tokens / denom

    def savings_usd(self, tier: TierCacheTokens) -> float:
        """USD saved vs no-cache pricing: read*0.9 - create*0.25 (input rate).

        Cache reads cost ~10% of normal input pricing (so 90% saved).
        Cache creation costs ~125% of normal input (so 25% extra paid).
        Net savings = read * input_rate * 0.9 - create * input_rate * 0.25.
        """
        if not tier.model or (tier.create_tokens + tier.read_tokens) == 0:
            return 0.0
        # USD per 1M input tokens for the tier's model, then per-token rate.
        per_mtok = estimate_cost_usd(
            model=tier.model, input_tokens=1_000_000, output_tokens=0,
        )
        return (
            tier.read_tokens * per_mtok * _CACHE_READ_DISCOUNT
            - tier.create_tokens * per_mtok * _CACHE_CREATE_PREMIUM
        ) / 1_000_000.0
