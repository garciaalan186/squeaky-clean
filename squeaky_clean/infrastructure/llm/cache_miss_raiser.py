"""CacheMissRaiser: the inner gateway for --replay-only runs (R5.7)."""

from __future__ import annotations

from squeaky_clean.domain.interfaces.llm_gateway import LLMGateway
from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.domain.interfaces.llm_response import LLMResponse
from squeaky_clean.infrastructure.llm.replay_cache_miss_error import (
    ReplayCacheMissError,
)


class CacheMissRaiser(LLMGateway):
    """Slots in where the live gateway would sit; any call = cache miss.

    CachingLLMGateway only invokes its inner gateway when the cache has no
    entry, so wiring this as the inner makes every miss raise loudly with
    enough context (model + key prefix + prompt head) to diagnose which
    prompt drifted.
    """

    def complete(self, request: LLMRequest) -> LLMResponse:
        """Always raises — a replay-only run must never reach the API."""
        head = request.user_prompt[:120].replace("\n", " ")
        raise ReplayCacheMissError(
            f"cache miss in --replay-only run: model={request.model} "
            f"key={request.cache_key()[:16]} prompt-head={head!r}"
        )
