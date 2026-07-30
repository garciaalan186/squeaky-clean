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

    ``architect`` is excluded from the default (R3.5): it runs once per problem
    with a unique prompt, so anchoring it only pays the ~25% cache-creation
    premium with no later read to amortise it — measured as a 0% hit-ratio and
    negative savings. The tiers that DO repeat identical system prompts
    (``icp`` reuses one of 34 stable pattern specs per call; ``manager`` and
    ``fixer`` recur per module/failure) stay on. Add ``architect`` back
    explicitly if a workload re-invokes it enough to amortise the premium.
    """

    enabled: bool = True
    enabled_tiers: tuple[str, ...] = ("manager", "icp", "fixer")

    def __post_init__(self) -> None:
        for t in self.enabled_tiers:
            if t not in _KNOWN_TIERS:
                raise ValueError(
                    f"unknown tier {t!r}; must be one of {sorted(_KNOWN_TIERS)}"
                )

    def is_enabled_for(self, tier: str) -> bool:
        """Return True iff caching is on AND ``tier`` is in the allowlist."""
        return self.enabled and tier in self.enabled_tiers
