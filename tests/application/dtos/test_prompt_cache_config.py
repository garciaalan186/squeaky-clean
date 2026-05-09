"""Unit tests for PromptCacheConfig DTO."""

import pytest

from squeaky_clean.application.dtos.prompt_cache_config import PromptCacheConfig


def test_defaults_enable_all_four_tiers() -> None:
    cfg = PromptCacheConfig()
    assert cfg.enabled is True
    assert set(cfg.enabled_tiers) == {
        "architect", "manager", "icp", "fixer",
    }
    for t in ("architect", "manager", "icp", "fixer"):
        assert cfg.is_enabled_for(t) is True


def test_global_disable_overrides_tier_allowlist() -> None:
    cfg = PromptCacheConfig(enabled=False)
    for t in ("architect", "manager", "icp", "fixer"):
        assert cfg.is_enabled_for(t) is False


def test_tier_allowlist_restricts_when_enabled() -> None:
    cfg = PromptCacheConfig(enabled=True, enabled_tiers=("architect", "icp"))
    assert cfg.is_enabled_for("architect") is True
    assert cfg.is_enabled_for("icp") is True
    assert cfg.is_enabled_for("manager") is False
    assert cfg.is_enabled_for("fixer") is False


def test_unknown_tier_raises_value_error() -> None:
    with pytest.raises(ValueError, match="unknown tier"):
        PromptCacheConfig(enabled_tiers=("architect", "bogus"))


def test_is_immutable() -> None:
    cfg = PromptCacheConfig()
    with pytest.raises(AttributeError):
        cfg.enabled = False  # type: ignore[misc]
