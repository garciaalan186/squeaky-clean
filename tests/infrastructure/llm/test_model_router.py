"""Tests for ModelRouter."""

from squeaky_clean.domain.value_objects.model_tier import ModelTier
from squeaky_clean.infrastructure.llm.model_catalog import ModelId
from squeaky_clean.infrastructure.llm.model_router import ModelRouter


def test_default_mapping_routes_all_tiers() -> None:
    router = ModelRouter()
    # Asserted via the ModelId SSOT so a version bump never re-breaks this.
    assert router.route(ModelTier.ARCHITECT) == ModelId.OPUS
    assert router.route(ModelTier.MANAGER) == ModelId.SONNET
    assert router.route(ModelTier.ICP) == ModelId.HAIKU
    assert router.route(ModelTier.FIXER) == ModelId.SONNET


def test_custom_mapping_overrides_default() -> None:
    router = ModelRouter(
        {
            ModelTier.ARCHITECT: "claude-sonnet-4-6",
            ModelTier.MANAGER: "claude-sonnet-4-6",
            ModelTier.ICP: "claude-haiku-4-5-20251001",
        }
    )
    assert router.route(ModelTier.ARCHITECT) == "claude-sonnet-4-6"
