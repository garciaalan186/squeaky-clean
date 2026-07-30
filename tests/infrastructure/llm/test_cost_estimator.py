"""Tests for estimate_request_cost (R2.6)."""

from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.infrastructure.llm.cost_estimator import estimate_request_cost
from squeaky_clean.infrastructure.llm.model_catalog import ModelId


def _req(**kw: object) -> LLMRequest:
    return LLMRequest(
        model=ModelId.HAIKU, system_prompt="s" * 400,
        user_prompt="u" * 400, **kw,  # type: ignore[arg-type]
    )


def test_estimate_is_positive_for_known_model() -> None:
    assert estimate_request_cost(_req()) > 0.0


def test_larger_max_tokens_costs_more() -> None:
    small = estimate_request_cost(_req(max_tokens=1000))
    large = estimate_request_cost(_req(max_tokens=8000))
    assert large > small


def test_longer_prompt_costs_more() -> None:
    short = estimate_request_cost(
        LLMRequest(model=ModelId.HAIKU, system_prompt="s", user_prompt="u"),
    )
    long = estimate_request_cost(_req())
    assert long > short
