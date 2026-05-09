"""Unit tests for CachingLLMGateway."""

from pathlib import Path

from squeaky_clean.domain.interfaces.llm_gateway import LLMGateway
from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.domain.interfaces.llm_response import LLMResponse
from squeaky_clean.infrastructure.llm.caching_llm_gateway import CachingLLMGateway


class _CountingGateway(LLMGateway):
    def __init__(self, response: LLMResponse) -> None:
        self._response = response
        self.calls = 0

    def complete(self, request: LLMRequest) -> LLMResponse:
        self.calls += 1
        return self._response


def _make_response(content: str = "ARCH-OUT") -> LLMResponse:
    return LLMResponse(
        content=content,
        input_tokens=10,
        output_tokens=20,
        cost_usd=0.001,
        duration_ms=150,
    )


def test_first_call_misses_cache(tmp_path: Path) -> None:
    inner = _CountingGateway(_make_response())
    gw = CachingLLMGateway(inner, tmp_path / "cache")
    out = gw.complete(LLMRequest("m", "sys", "user"))
    assert inner.calls == 1
    assert out.cache_hit is False
    assert out.content == "ARCH-OUT"


def test_repeat_call_hits_cache(tmp_path: Path) -> None:
    inner = _CountingGateway(_make_response())
    gw = CachingLLMGateway(inner, tmp_path / "cache")
    req = LLMRequest("m", "sys", "user")
    gw.complete(req)
    out = gw.complete(req)
    assert inner.calls == 1
    assert out.cache_hit is True
    assert out.cost_usd == 0.0
    assert out.duration_ms == 0


def test_replicate_id_busts_cache(tmp_path: Path) -> None:
    inner = _CountingGateway(_make_response())
    gw = CachingLLMGateway(inner, tmp_path / "cache")
    gw.complete(LLMRequest("m", "sys", "user", replicate_id=0))
    gw.complete(LLMRequest("m", "sys", "user", replicate_id=1))
    assert inner.calls == 2


def test_different_prompts_bust_cache(tmp_path: Path) -> None:
    inner = _CountingGateway(_make_response())
    gw = CachingLLMGateway(inner, tmp_path / "cache")
    gw.complete(LLMRequest("m", "sys", "user-a"))
    gw.complete(LLMRequest("m", "sys", "user-b"))
    assert inner.calls == 2


def test_timed_out_responses_not_cached(tmp_path: Path) -> None:
    timeout_resp = LLMResponse(
        content="", input_tokens=0, output_tokens=0,
        cost_usd=0.0, duration_ms=0, timed_out=True,
    )
    inner = _CountingGateway(timeout_resp)
    gw = CachingLLMGateway(inner, tmp_path / "cache")
    gw.complete(LLMRequest("m", "sys", "user"))
    gw.complete(LLMRequest("m", "sys", "user"))
    assert inner.calls == 2


def test_cache_key_is_stable() -> None:
    a = LLMRequest("m", "sys", "user")
    b = LLMRequest("m", "sys", "user")
    assert a.cache_key() == b.cache_key()


def test_cache_key_changes_on_temperature() -> None:
    a = LLMRequest("m", "sys", "user", temperature=0.0)
    b = LLMRequest("m", "sys", "user", temperature=0.7)
    assert a.cache_key() != b.cache_key()


