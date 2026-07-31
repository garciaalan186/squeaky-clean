"""CachingLLMGateway must not cache empty responses (R5.6 finding)."""

from pathlib import Path

from squeaky_clean.domain.interfaces.llm_gateway import LLMGateway
from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.domain.interfaces.llm_response import LLMResponse
from squeaky_clean.infrastructure.llm.caching_llm_gateway import CachingLLMGateway


class _Inner(LLMGateway):
    def __init__(self, content: str) -> None:
        self.calls = 0
        self._content = content

    def complete(self, request: LLMRequest) -> LLMResponse:
        self.calls += 1
        return LLMResponse(
            content=self._content, input_tokens=1, output_tokens=1,
            cost_usd=0.0, duration_ms=1,
        )


def _request() -> LLMRequest:
    return LLMRequest(model="m", system_prompt="s", user_prompt="u")


def test_empty_response_is_not_cached(tmp_path: Path) -> None:
    inner = _Inner("")
    gw = CachingLLMGateway(inner, tmp_path)
    gw.complete(_request())
    gw.complete(_request())
    assert inner.calls == 2  # second call NOT served from cache
    assert list(tmp_path.glob("*.json")) == []


def test_real_response_is_cached(tmp_path: Path) -> None:
    inner = _Inner("MODULE X")
    gw = CachingLLMGateway(inner, tmp_path)
    gw.complete(_request())
    assert gw.complete(_request()).content == "MODULE X"
    assert inner.calls == 1
