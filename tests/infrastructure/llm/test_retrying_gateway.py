"""Tests for RetryingGateway transient-failure handling (R0.8)."""

import pytest

from squeaky_clean.application.shared.gateways.retry_policy import RetryPolicy
from squeaky_clean.domain.interfaces.llm_gateway import LLMGateway
from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.domain.interfaces.llm_response import LLMResponse
from squeaky_clean.infrastructure.llm.llm_gateway_error import LLMGatewayError
from squeaky_clean.infrastructure.llm.retrying_gateway import RetryingGateway

_POLICY = RetryPolicy(max_transport_retries=2, backoff_base_seconds=0.0)


def _req() -> LLMRequest:
    return LLMRequest(model="m", system_prompt="s", user_prompt="u")


def _ok(content: str = "ok") -> LLMResponse:
    return LLMResponse(
        content=content, input_tokens=1, output_tokens=1,
        cost_usd=0.01, duration_ms=1,
    )


class _Scripted(LLMGateway):
    """Yields queued outcomes; an exception instance is raised, else returned."""

    def __init__(self, outcomes: list[object]) -> None:
        self._outcomes = outcomes
        self.calls = 0

    def complete(self, request: LLMRequest) -> LLMResponse:
        outcome = self._outcomes[self.calls]
        self.calls += 1
        if isinstance(outcome, Exception):
            raise outcome
        assert isinstance(outcome, LLMResponse)
        return outcome


def _gateway(inner: LLMGateway) -> RetryingGateway:
    return RetryingGateway(inner, _POLICY, sleep=lambda _s: None, rand=lambda: 0.5)


def test_retryable_error_then_success() -> None:
    inner = _Scripted([LLMGatewayError("boom", retryable=True), _ok()])
    result = _gateway(inner).complete(_req())
    assert result.content == "ok"
    assert inner.calls == 2


def test_timeout_response_then_success() -> None:
    timed = LLMResponse(
        content="", input_tokens=0, output_tokens=0,
        cost_usd=0.0, duration_ms=1, timed_out=True,
    )
    inner = _Scripted([timed, _ok()])
    result = _gateway(inner).complete(_req())
    assert result.content == "ok"
    assert inner.calls == 2


def test_non_retryable_error_surfaces_immediately() -> None:
    inner = _Scripted([LLMGatewayError("is_error", retryable=False)])
    with pytest.raises(LLMGatewayError):
        _gateway(inner).complete(_req())
    assert inner.calls == 1  # no retry burned


def test_retries_exhausted_reraises_last_error() -> None:
    inner = _Scripted([LLMGatewayError("boom", retryable=True)] * 3)
    with pytest.raises(LLMGatewayError):
        _gateway(inner).complete(_req())
    assert inner.calls == 3  # initial + 2 retries


def test_persistent_timeout_returns_timed_out_response() -> None:
    timed = LLMResponse(
        content="", input_tokens=0, output_tokens=0,
        cost_usd=0.0, duration_ms=1, timed_out=True,
    )
    inner = _Scripted([timed, timed, timed])
    result = _gateway(inner).complete(_req())
    assert result.timed_out is True  # handed up for agent_hangs accounting
    assert inner.calls == 3


def test_jitter_is_deterministic_given_rand() -> None:
    # base delay_for(0) = 2.0; jitter_ratio 0.5; rand 1.0 → 2.0 + 1.0*0.5*2.0 = 3.0
    p = RetryPolicy(backoff_base_seconds=2.0, backoff_multiplier=3.0, jitter_ratio=0.5)
    assert p.jittered_delay_for(0, 1.0) == 3.0
    assert p.jittered_delay_for(0, 0.0) == 2.0
