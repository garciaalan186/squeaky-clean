"""Tests for the TierCacheTokens value object."""

import pytest

from squeaky_clean.application.evaluation.eval.metrics.tier_cache_tokens import (
    TierCacheTokens,
)


def test_holds_totals_and_model() -> None:
    tier = TierCacheTokens(create_tokens=7, read_tokens=3, model="claude-haiku-4-5")
    assert tier.create_tokens == 7
    assert tier.read_tokens == 3
    assert tier.model == "claude-haiku-4-5"


def test_is_frozen() -> None:
    tier = TierCacheTokens(create_tokens=1, read_tokens=2, model="m")
    with pytest.raises(AttributeError):
        tier.read_tokens = 5  # type: ignore[misc]
