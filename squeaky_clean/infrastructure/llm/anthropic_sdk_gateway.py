"""AnthropicSDKGateway: LLMGateway adapter using the official Anthropic SDK.

Attaches ephemeral ``cache_control`` blocks on the system prompt and on a
stable user-prompt prefix when the request's tier is enabled in the
PromptCacheConfig — so repeated sibling/replicate calls share the cached
prefix across the 5-minute Anthropic window.
"""

from __future__ import annotations

import os
import time

import anthropic

from squeaky_clean.application.shared.gateways.prompt_cache_config import PromptCacheConfig
from squeaky_clean.domain.interfaces.llm_gateway import LLMGateway
from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.domain.interfaces.llm_response import LLMResponse
from squeaky_clean.domain.interfaces.run_logger import NullRunLogger, RunLogger
from squeaky_clean.infrastructure.llm.anthropic_prompt_blocks import AnthropicPromptBlocks
from squeaky_clean.infrastructure.llm.anthropic_response_mapper import (
    AnthropicResponseMapper,
)
from squeaky_clean.infrastructure.llm.llm_gateway_error import LLMGatewayError
from squeaky_clean.infrastructure.llm.token_bucket_rate_limiter import (
    TokenBucketRateLimiter,
)

_DEFAULT_MAX_TOKENS: int = 4096
_DEFAULT_TIMEOUT: float = 240.0
_DEFAULT_RPS: float = 4.0
_DEFAULT_BURST: int = 8
_DEFAULT_TEMPERATURE: float = 0.0


class AnthropicSDKGateway(LLMGateway):
    """Direct-SDK gateway with per-tier ephemeral prompt caching."""

    def __init__(
        self,
        api_key: str | None = None,
        graceful_timeout: bool = True,
        max_tokens: int = _DEFAULT_MAX_TOKENS,
        rate_limiter: TokenBucketRateLimiter | None = None,
        prompt_cache_config: PromptCacheConfig | None = None,
        logger: RunLogger | None = None,
    ) -> None:
        key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        if not key:
            raise LLMGatewayError("ANTHROPIC_API_KEY not set")
        self._client: anthropic.Anthropic = anthropic.Anthropic(
            api_key=key, timeout=_DEFAULT_TIMEOUT,
        )
        self._graceful: bool = graceful_timeout
        self._max_tokens: int = max_tokens
        # R6.12-audited defaults: in-memory throttle (no I/O at construction)
        # and a frozen config VO — both stay injectable for tests/wiring.
        self._limiter: TokenBucketRateLimiter = (
            rate_limiter
            if rate_limiter is not None
            else TokenBucketRateLimiter(
                capacity=_DEFAULT_BURST, refill_per_second=_DEFAULT_RPS,
            )
        )
        self._cache_cfg: PromptCacheConfig = (
            prompt_cache_config
            if prompt_cache_config is not None
            else PromptCacheConfig()
        )
        self._log: RunLogger = logger or NullRunLogger()
        self._blocks: AnthropicPromptBlocks = AnthropicPromptBlocks()
        self._mapper: AnthropicResponseMapper = AnthropicResponseMapper(self._log)
        self._seed_noted: bool = False

    def complete(self, request: LLMRequest) -> LLMResponse:
        """Call messages.create with optional cache_control blocks."""
        self._limiter.acquire()
        start = time.monotonic()
        if request.seed is not None and not self._seed_noted:
            # Once per gateway instance (was a per-call DEBUG record).
            self._seed_noted = True
            self._log.event(
                "sdk_sampling_knobs_ignored", seed=request.seed,
                detail="Anthropic API accepts no seed; temperature is "
                       "deprecated on current models — model defaults used",
            )
        cache_on = self._cache_enabled_for(request)
        try:
            msg = self._client.messages.create(
                model=request.model,
                max_tokens=request.max_tokens or self._max_tokens,
                system=self._blocks.build_system(request, cache_on),
                messages=self._blocks.build_messages(request, cache_on),
            )
        except anthropic.APITimeoutError as exc:
            if self._graceful:
                return LLMResponse(
                    content="", input_tokens=0, output_tokens=0,
                    cost_usd=0.0,
                    duration_ms=int((time.monotonic() - start) * 1000),
                    timed_out=True,
                )
            raise LLMGatewayError(f"sdk timeout: {exc}") from exc
        except anthropic.APIError as exc:
            raise LLMGatewayError(f"anthropic api error: {exc}") from exc
        return self._mapper.map(msg, start)

    def _cache_enabled_for(self, request: LLMRequest) -> bool:
        if request.tier is None:
            return self._cache_cfg.enabled
        return self._cache_cfg.is_enabled_for(request.tier)
