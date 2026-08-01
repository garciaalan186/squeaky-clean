"""Tests for the TierCacheStats value object."""

import dataclasses

import pytest

from squeaky_clean.application.evaluation.eval.metrics.model.tier_cache_stats import TierCacheStats


def test_defaults_are_empty() -> None:
    s = TierCacheStats()
    assert (s.create_tokens, s.read_tokens, s.savings_usd) == (0, 0, 0.0)
    assert s.hit_ratio == 0.0


def test_hit_ratio_is_read_share() -> None:
    s = TierCacheStats(create_tokens=1_200, read_tokens=4_800)
    assert s.hit_ratio == pytest.approx(0.8)


def test_hit_ratio_zero_when_no_activity() -> None:
    assert TierCacheStats(savings_usd=0.5).hit_ratio == 0.0


def test_combined_sums_elementwise_and_ratio_recomputes() -> None:
    a = TierCacheStats(create_tokens=100, read_tokens=300, savings_usd=0.01)
    b = TierCacheStats(create_tokens=100, read_tokens=100, savings_usd=0.02)
    c = a.combined(b)
    assert (c.create_tokens, c.read_tokens) == (200, 400)
    assert c.savings_usd == pytest.approx(0.03)
    assert c.hit_ratio == pytest.approx(400 / 600)


def test_is_frozen() -> None:
    s = TierCacheStats()
    with pytest.raises(dataclasses.FrozenInstanceError):
        s.create_tokens = 1  # type: ignore[misc]


def test_serializes_via_asdict() -> None:
    s = TierCacheStats(create_tokens=7, read_tokens=3, savings_usd=0.1)
    assert dataclasses.asdict(s) == {
        "create_tokens": 7, "read_tokens": 3, "savings_usd": 0.1,
    }
