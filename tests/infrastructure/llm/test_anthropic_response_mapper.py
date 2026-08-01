"""Unit tests for AnthropicResponseMapper (extracted from the SDK gateway)."""

from __future__ import annotations

import time
from typing import cast

import anthropic

from squeaky_clean.domain.interfaces.llm_response import LLMResponse
from squeaky_clean.infrastructure.llm.anthropic_response_mapper import (
    AnthropicResponseMapper,
)


class _FakeUsage:
    input_tokens = 10
    output_tokens = 5
    cache_creation_input_tokens = 3
    cache_read_input_tokens = 7


class _FakeContentBlock:
    def __init__(self, text: str) -> None:
        self.text = text


class _FakeMessage:
    def __init__(self, stop_reason: str = "end_turn") -> None:
        self.model = "claude-haiku-4-5-20251001"
        self.usage = _FakeUsage()
        self.content = [_FakeContentBlock("ok")]
        self.stop_reason = stop_reason


def _map(msg: _FakeMessage) -> LLMResponse:
    return AnthropicResponseMapper().map(
        cast("anthropic.types.Message", msg), time.monotonic(),
    )


def test_maps_text_and_folds_cache_tokens_into_input_total() -> None:
    response = _map(_FakeMessage())
    assert response.content == "ok"
    assert response.input_tokens == 20
    assert response.output_tokens == 5
    assert response.cache_creation_input_tokens == 3
    assert response.cache_read_input_tokens == 7


def test_cost_is_positive_for_known_model() -> None:
    assert _map(_FakeMessage()).cost_usd > 0.0


def test_max_tokens_stop_reason_marks_truncated() -> None:
    assert _map(_FakeMessage("max_tokens")).truncated
    assert not _map(_FakeMessage()).truncated
