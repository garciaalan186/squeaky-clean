"""Tests for CacheMissRaiser + ReplayCacheMissError (R5.7)."""

import pytest

from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.infrastructure.llm.cache_miss_raiser import CacheMissRaiser
from squeaky_clean.infrastructure.llm.replay_cache_miss_error import (
    ReplayCacheMissError,
)


def _request() -> LLMRequest:
    return LLMRequest(
        model="claude-haiku-4-5-20251001",
        system_prompt="spec", user_prompt="CLASS Cart\nPATTERN Entity",
    )


def test_any_call_raises_with_diagnostic_context() -> None:
    with pytest.raises(ReplayCacheMissError) as exc:
        CacheMissRaiser().complete(_request())
    msg = str(exc.value)
    assert "replay-only" in msg
    assert "claude-haiku" in msg
    assert "CLASS Cart" in msg  # prompt head, newline-flattened


def test_cached_entry_is_served_without_raising(tmp_path) -> None:  # noqa: ANN001
    from squeaky_clean.infrastructure.llm.caching_llm_gateway import (
        CachingLLMGateway,
    )
    gw = CachingLLMGateway(CacheMissRaiser(), tmp_path)
    request = _request()
    (tmp_path / f"{request.cache_key()}.json").write_text(
        '{"content": "cached code"}',
    )
    assert gw.complete(request).content == "cached code"
