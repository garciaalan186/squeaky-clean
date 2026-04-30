"""AnthropicSDKGateway: LLMGateway adapter using the official Anthropic SDK.

Attaches ephemeral ``cache_control`` blocks on the system prompt and on a
stable user-prompt prefix when the request's tier is enabled in the
PromptCacheConfig — so repeated sibling/replicate calls share the cached
prefix across the 5-minute Anthropic window.
"""

from __future__ import annotations

import logging
import os
import time

import anthropic
from anthropic.types import MessageParam, TextBlockParam

from squeaky_clean.application.dtos.prompt_cache_config import PromptCacheConfig
from squeaky_clean.domain.interfaces.llm_gateway import LLMGateway
from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.domain.interfaces.llm_response import LLMResponse
from squeaky_clean.infrastructure.llm.llm_gateway_error import LLMGatewayError
from squeaky_clean.infrastructure.llm.model_pricing import estimate_cost_usd
from squeaky_clean.infrastructure.llm.token_bucket_rate_limiter import (
    TokenBucketRateLimiter,
)

_DEFAULT_MAX_TOKENS: int = 4096
_DEFAULT_TIMEOUT: float = 240.0
_DEFAULT_RPS: float = 4.0
_DEFAULT_BURST: int = 8
_DEFAULT_TEMPERATURE: float = 0.0
_LOG = logging.getLogger(__name__)


class AnthropicSDKGateway(LLMGateway):
    """Direct-SDK gateway with per-tier ephemeral prompt caching."""

    def __init__(
        self,
        api_key: str | None = None,
        graceful_timeout: bool = True,
        max_tokens: int = _DEFAULT_MAX_TOKENS,
        rate_limiter: TokenBucketRateLimiter | None = None,
        prompt_cache_config: PromptCacheConfig | None = None,
    ) -> None:
        key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        if not key:
            raise LLMGatewayError("ANTHROPIC_API_KEY not set")
        self._client: anthropic.Anthropic = anthropic.Anthropic(
            api_key=key, timeout=_DEFAULT_TIMEOUT,
        )
        self._graceful: bool = graceful_timeout
        self._max_tokens: int = max_tokens
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

    def complete(self, request: LLMRequest) -> LLMResponse:
        """Call messages.create with optional cache_control blocks."""
        self._limiter.acquire()
        start = time.monotonic()
        temperature = (
            request.temperature if request.temperature is not None
            else _DEFAULT_TEMPERATURE
        )
        if request.seed is not None:
            _LOG.debug(
                "Anthropic API does not accept seed=%s; relying on temperature"
                "=%s for determinism", request.seed, temperature,
            )
        cache_on = self._cache_enabled_for(request)
        try:
            msg = self._client.messages.create(
                model=request.model,
                max_tokens=self._max_tokens,
                temperature=temperature,
                system=self._build_system(request, cache_on),
                messages=self._build_messages(request, cache_on),
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
        return self._build_response(msg, start)

    def _cache_enabled_for(self, request: LLMRequest) -> bool:
        if request.tier is None:
            return self._cache_cfg.enabled
        return self._cache_cfg.is_enabled_for(request.tier)

    def _build_system(
        self, request: LLMRequest, cache_on: bool,
    ) -> list[TextBlockParam]:
        if cache_on:
            block: TextBlockParam = {
                "type": "text", "text": request.system_prompt,
                "cache_control": {"type": "ephemeral"},
            }
        else:
            block = {"type": "text", "text": request.system_prompt}
        return [block]

    def _build_messages(
        self, request: LLMRequest, cache_on: bool,
    ) -> list[MessageParam]:
        prefix = request.cacheable_user_prefix
        if not cache_on or not prefix:
            return [{"role": "user", "content": request.user_prompt}]
        suffix = request.user_prompt[len(prefix):] if (
            request.user_prompt.startswith(prefix)
        ) else request.user_prompt
        prefix_block: TextBlockParam = {
            "type": "text", "text": prefix,
            "cache_control": {"type": "ephemeral"},
        }
        suffix_block: TextBlockParam = {"type": "text", "text": suffix}
        return [{"role": "user", "content": [prefix_block, suffix_block]}]

    def _build_response(
        self, msg: anthropic.types.Message, start: float,
    ) -> LLMResponse:
        text = self._extract_text(msg)
        usage = msg.usage
        cache_create = int(getattr(usage, "cache_creation_input_tokens", 0) or 0)
        cache_read = int(getattr(usage, "cache_read_input_tokens", 0) or 0)
        plain_in = int(usage.input_tokens)
        out = int(usage.output_tokens)
        cost = estimate_cost_usd(
            model=str(msg.model),
            input_tokens=plain_in,
            output_tokens=out,
            cache_creation_tokens=cache_create,
            cache_read_tokens=cache_read,
        )
        return LLMResponse(
            content=text,
            input_tokens=plain_in + cache_create + cache_read,
            output_tokens=out,
            cost_usd=cost,
            duration_ms=int((time.monotonic() - start) * 1000),
            cache_creation_input_tokens=cache_create,
            cache_read_input_tokens=cache_read,
        )

    def _extract_text(self, msg: anthropic.types.Message) -> str:
        for block in msg.content:
            text = getattr(block, "text", None)
            if isinstance(text, str):
                return text
        return ""
