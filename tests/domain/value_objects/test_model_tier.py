"""Tests for ModelTier."""

from squeaky_clean.domain.value_objects.model_tier import ModelTier


def test_model_tier_has_four_members() -> None:
    assert set(ModelTier) == {
        ModelTier.ARCHITECT,
        ModelTier.MANAGER,
        ModelTier.ICP,
        ModelTier.FIXER,
    }
