"""Tests for RouterFactory."""

from squeaky_clean.domain.value_objects.model_tier import ModelTier
from squeaky_clean.interface.cli.router_factory import RouterFactory


def test_phase5_default_routes_every_tier() -> None:
    """Regression: every ModelTier must be routable, including FIXER."""
    router = RouterFactory().build(None)
    for tier in ModelTier:
        assert router.route(tier), f"tier {tier} unrouted"


def test_override_forces_all_tiers_to_one_model() -> None:
    router = RouterFactory().build("claude-haiku-4-5-20251001")
    for tier in ModelTier:
        assert router.route(tier) == "claude-haiku-4-5-20251001"
