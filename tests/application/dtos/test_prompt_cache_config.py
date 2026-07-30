"""Unit tests for PromptCacheConfig DTO."""

import pytest

from squeaky_clean.application.shared.gateways.prompt_cache_config import PromptCacheConfig


def test_defaults_cache_repeating_tiers_but_not_architect() -> None:
    # R3.5: architect runs once/problem with a unique prompt → not cached by
    # default (0% hit, negative savings); the repeating tiers stay on.
    cfg = PromptCacheConfig()
    assert cfg.enabled is True
    assert set(cfg.enabled_tiers) == {"manager", "icp", "fixer"}
    for t in ("manager", "icp", "fixer"):
        assert cfg.is_enabled_for(t) is True
    assert cfg.is_enabled_for("architect") is False


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
