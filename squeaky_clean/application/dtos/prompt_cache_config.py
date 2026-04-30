"""PromptCacheConfig DTO: which agent tiers attach Anthropic cache_control."""

from __future__ import annotations

from dataclasses import dataclass

_KNOWN_TIERS: frozenset[str] = frozenset(
    {"architect", "manager", "icp", "fixer"}
)


@dataclass(frozen=True)
class PromptCacheConfig:
    """Toggle ephemeral prompt caching globally and per-tier.

    When ``enabled`` is False, no tier attaches ``cache_control`` regardless
    of ``enabled_tiers``. When ``enabled`` is True, only tiers listed in
    ``enabled_tiers`` get ``cache_control`` blocks attached to the system
    prompt + stable user-prompt prefix.
    """

    enabled: bool = True
    enabled_tiers: tuple[str, ...] = (
        "architect", "manager", "icp", "fixer",
    )

    def __post_init__(self) -> None:
        for t in self.enabled_tiers:
            if t not in _KNOWN_TIERS:
                raise ValueError(
                    f"unknown tier {t!r}; must be one of {sorted(_KNOWN_TIERS)}"
                )

    def is_enabled_for(self, tier: str) -> bool:
        """Return True iff caching is on AND ``tier`` is in the allowlist."""
        return self.enabled and tier in self.enabled_tiers
