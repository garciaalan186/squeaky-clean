"""Tests for InstantiatedICPPrompt DTO (H2)."""

from __future__ import annotations

from squeaky_clean.application.dtos.instantiated_icp_prompt import InstantiatedICPPrompt
from squeaky_clean.domain.value_objects.model_tier import ModelTier


def test_basic_construction() -> None:
    p = InstantiatedICPPrompt(
        system_prompt="sys", user_prompt="usr", model_tier=ModelTier.ICP,
    )
    assert p.system_prompt == "sys"
    assert p.user_prompt == "usr"
    assert p.model_tier is ModelTier.ICP
