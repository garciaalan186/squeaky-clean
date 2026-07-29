"""Tests for ModelPricing unknown-model fallback (R0.10)."""

from squeaky_clean.infrastructure.llm import model_pricing
from squeaky_clean.infrastructure.llm.model_catalog import ModelId
from squeaky_clean.infrastructure.llm.model_pricing import (
    _resolve_rates,
    estimate_cost_usd,
)


def test_known_model_prices_normally() -> None:
    cost = estimate_cost_usd(ModelId.HAIKU, 1_000_000, 0)
    assert cost > 0.0


def test_unknown_model_never_prices_zero() -> None:
    # A future/unknown model id must not silently contribute $0 to the budget.
    cost = estimate_cost_usd("claude-opus-9-future", 1_000_000, 1_000_000)
    assert cost > 0.0


def test_unknown_model_infers_family_from_substring() -> None:
    assert _resolve_rates("something-haiku-unknown") == model_pricing._FALLBACK[
        ModelId.HAIKU
    ]
    assert _resolve_rates("something-sonnet-unknown") == model_pricing._FALLBACK[
        ModelId.SONNET
    ]


def test_unrecognised_family_defaults_to_conservative_opus() -> None:
    # No family hint → most expensive tier, so budgets over-estimate not under.
    assert _resolve_rates("mystery-model-x") == model_pricing._FALLBACK[
        ModelId.OPUS
    ]
