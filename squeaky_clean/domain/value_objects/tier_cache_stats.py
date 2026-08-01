"""TierCacheStats value object: prompt-cache totals for one model tier."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TierCacheStats:
    """Immutable cache create/read token totals plus USD savings for a tier.

    The hit ratio is computed, never stored, so the invariant
    ``hit_ratio == read / (create + read)`` cannot drift (R6.3).
    """

    create_tokens: int = 0
    read_tokens: int = 0
    savings_usd: float = 0.0

    @property
    def hit_ratio(self) -> float:
        """Cache read share: read / (create + read); 0.0 with no activity."""
        denom = self.create_tokens + self.read_tokens
        if denom <= 0:
            return 0.0
        return self.read_tokens / denom

    def combined(self, other: TierCacheStats) -> TierCacheStats:
        """Return the element-wise sum of two stats (ratio recomputes)."""
        return TierCacheStats(
            create_tokens=self.create_tokens + other.create_tokens,
            read_tokens=self.read_tokens + other.read_tokens,
            savings_usd=self.savings_usd + other.savings_usd,
        )
