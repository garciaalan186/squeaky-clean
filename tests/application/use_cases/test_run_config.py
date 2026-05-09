"""Tests for RunConfig."""

from squeaky_clean.application.use_cases.run_config import RunConfig
from squeaky_clean.domain.value_objects.model_tier import ModelTier


def test_default_run_config_uses_default_policy() -> None:
    rc = RunConfig()
    assert rc.seed == 0
    assert rc.replicate_id == 0
    assert rc.sampling_for(ModelTier.ARCHITECT).temperature == 0.0
    assert rc.sampling_for(ModelTier.ICP).temperature == 0.2


def test_run_config_seed_threaded_into_icp_sampling() -> None:
    rc = RunConfig(seed=42)
    assert rc.sampling_for(ModelTier.ICP).seed == 42
    assert rc.sampling_for(ModelTier.ARCHITECT).seed == 0


def test_deterministic_factory_zeros_all_tiers() -> None:
    rc = RunConfig.deterministic(replicate_id=3)
    assert rc.replicate_id == 3
    for tier in ModelTier:
        s = rc.sampling_for(tier)
        assert s.temperature == 0.0
        assert s.seed == 0
