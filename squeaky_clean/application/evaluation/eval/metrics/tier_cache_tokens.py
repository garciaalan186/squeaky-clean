"""TierCacheTokens: cache create/read token totals for one model tier."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TierCacheTokens:
    """Cache create/read totals plus the model used for one tier."""

    create_tokens: int
    read_tokens: int
    model: str
