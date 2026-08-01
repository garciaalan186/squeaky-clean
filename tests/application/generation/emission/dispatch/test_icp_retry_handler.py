"""Tests for ICPRetryHandler retry/backoff behavior (no real sleeping)."""

from squeaky_clean.application.generation.emission.dispatch.icp_retry_handler import (
    ICPRetryHandler,
)
from squeaky_clean.application.shared.gateways.retry_policy import RetryPolicy
from squeaky_clean.domain.interfaces.llm_gateway import LLMGateway
from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.domain.interfaces.llm_response import LLMResponse

_GOOD = "```python\nclass Foo:\n    pass\n```"
_BAD = "sorry, no code here"
_POLICY = RetryPolicy(max_icp_retries=2, backoff_base_seconds=0.0)


class _ScriptedGateway(LLMGateway):
    """Returns queued responses in order and records every request."""

    def __init__(self, responses: list[LLMResponse]) -> None:
        self.requests: list[LLMRequest] = []
        self._responses: list[LLMResponse] = list(responses)

    def complete(self, request: LLMRequest) -> LLMResponse:
        self.requests.append(request)
        return self._responses.pop(0)


def _response(content: str, timed_out: bool = False) -> LLMResponse:
    return LLMResponse(
        content=content, input_tokens=1, output_tokens=1, cost_usd=0.0,
        duration_ms=1, timed_out=timed_out,
    )


def _request() -> LLMRequest:
    return LLMRequest(model="m", system_prompt="sys", user_prompt="implement Foo")


def test_parseable_first_response_needs_no_retry() -> None:
    gateway = _ScriptedGateway([])
    first = _response(_GOOD)
    result, attempts = ICPRetryHandler(gateway, _POLICY).run(_request(), "Foo", first)
    assert (result, attempts) == (first, 0)
    assert gateway.requests == []


def test_parse_failure_retries_with_error_appended_to_prompt() -> None:
    gateway = _ScriptedGateway([_response(_GOOD)])
    result, attempts = ICPRetryHandler(gateway, _POLICY).run(
        _request(), "Foo", _response(_BAD),
    )
    assert attempts == 1
    assert result.content == _GOOD
    retry_prompt = gateway.requests[0].user_prompt
    assert retry_prompt.startswith("implement Foo")
    assert "RETRY" in retry_prompt


def test_timed_out_first_response_triggers_retry() -> None:
    gateway = _ScriptedGateway([_response(_GOOD)])
    _, attempts = ICPRetryHandler(gateway, _POLICY).run(
        _request(), "Foo", _response("", timed_out=True),
    )
    assert attempts == 1
    assert "timed out" in gateway.requests[0].user_prompt


def test_exhausted_retries_returns_last_response_and_max_count() -> None:
    last = _response(_BAD)
    gateway = _ScriptedGateway([_response(_BAD), last])
    result, attempts = ICPRetryHandler(gateway, _POLICY).run(
        _request(), "Foo", _response(_BAD),
    )
    assert attempts == _POLICY.max_icp_retries
    assert result is last
    assert len(gateway.requests) == 2
