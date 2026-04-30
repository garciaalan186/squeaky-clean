"""Tests for LLMResponse."""

from squeaky_clean.domain.interfaces.llm_response import LLMResponse


def test_llm_response_stores_all_fields() -> None:
    resp = LLMResponse(
        content="ok",
        input_tokens=10,
        output_tokens=5,
        cost_usd=0.001,
        duration_ms=42,
    )
    assert resp.content == "ok"
    assert resp.input_tokens == 10
    assert resp.output_tokens == 5
    assert resp.cost_usd == 0.001
    assert resp.duration_ms == 42
