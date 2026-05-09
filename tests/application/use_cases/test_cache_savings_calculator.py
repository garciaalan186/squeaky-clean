"""Unit tests for CacheSavingsCalculator (hit ratio + USD savings math)."""

import pytest

from squeaky_clean.application.use_cases.cache_savings_calculator import (
    CacheSavingsCalculator,
    TierCacheTokens,
)


def test_hit_ratio_zero_when_no_activity() -> None:
    calc = CacheSavingsCalculator()
    assert calc.hit_ratio(TierCacheTokens(0, 0, "claude-haiku-4-5")) == 0.0


def test_hit_ratio_pure_read() -> None:
    calc = CacheSavingsCalculator()
    assert calc.hit_ratio(
        TierCacheTokens(0, 1000, "claude-haiku-4-5")
    ) == 1.0


def test_hit_ratio_mixed() -> None:
    calc = CacheSavingsCalculator()
    r = calc.hit_ratio(TierCacheTokens(200, 800, "claude-haiku-4-5"))
    assert r == pytest.approx(0.8, rel=1e-9)


def test_savings_pure_read_haiku() -> None:
    # Haiku input rate = $1.0 per 1M tok.
    # 10_000 read tokens * $1.0 / 1M * 0.9 saved = $0.009
    calc = CacheSavingsCalculator()
    s = calc.savings_usd(TierCacheTokens(0, 10_000, "claude-haiku-4-5"))
    assert s == pytest.approx(0.009, rel=1e-3)


def test_savings_pure_create_haiku_is_negative() -> None:
    # Cache create costs 0.25x extra: 10_000 * 1.0/1M * 0.25 = $0.0025 paid.
    calc = CacheSavingsCalculator()
    s = calc.savings_usd(TierCacheTokens(10_000, 0, "claude-haiku-4-5"))
    assert s == pytest.approx(-0.0025, rel=1e-3)


def test_savings_zero_for_unknown_model() -> None:
    calc = CacheSavingsCalculator()
    s = calc.savings_usd(TierCacheTokens(1000, 1000, "model-not-priced"))
    assert s == 0.0


def test_savings_zero_when_empty_model_string() -> None:
    calc = CacheSavingsCalculator()
    s = calc.savings_usd(TierCacheTokens(1000, 1000, ""))
    assert s == 0.0


def test_savings_sonnet_higher_per_token() -> None:
    # Sonnet $3/M; net savings should be ~3x haiku for same token mix.
    calc = CacheSavingsCalculator()
    haiku = calc.savings_usd(TierCacheTokens(0, 100_000, "claude-haiku-4-5"))
    sonnet = calc.savings_usd(
        TierCacheTokens(0, 100_000, "claude-sonnet-4-6"),
    )
    assert sonnet == pytest.approx(haiku * 3.0, rel=1e-6)
