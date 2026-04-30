"""Tests for TemperaturePolicy."""

from squeaky_clean.domain.value_objects.model_tier import ModelTier
from squeaky_clean.infrastructure.llm.temperature_policy import TemperaturePolicy


def test_default_policy_architect_is_zero_seeded() -> None:
    p = TemperaturePolicy.default()
    a = p.for_tier(ModelTier.ARCHITECT)
    assert a.temperature == 0.0
    assert a.seed == 0


def test_default_policy_icp_is_sampled() -> None:
    p = TemperaturePolicy.default()
    icp = p.for_tier(ModelTier.ICP)
    assert icp.temperature == 0.2
    assert icp.seed == 0


def test_default_policy_manager_and_fixer_deterministic() -> None:
    p = TemperaturePolicy.default()
    assert p.for_tier(ModelTier.MANAGER).temperature == 0.0
    assert p.for_tier(ModelTier.FIXER).temperature == 0.0


def test_deterministic_policy_pins_all_tiers() -> None:
    p = TemperaturePolicy.deterministic()
    for tier in ModelTier:
        s = p.for_tier(tier)
        assert s.temperature == 0.0
        assert s.seed == 0
