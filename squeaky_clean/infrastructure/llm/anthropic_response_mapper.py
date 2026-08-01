"""AnthropicResponseMapper: SDK Message -> LLMResponse (usage + cost)."""

from __future__ import annotations

import time

import anthropic

from squeaky_clean.domain.interfaces.llm_response import LLMResponse
from squeaky_clean.domain.interfaces.run_logger import NullRunLogger, RunLogger
from squeaky_clean.infrastructure.llm.model_pricing import estimate_cost_usd


class AnthropicResponseMapper:
    """Maps a completed SDK message into the port-level LLMResponse."""

    def __init__(self, logger: RunLogger | None = None) -> None:
        self._log: RunLogger = logger or NullRunLogger()

    def map(self, msg: anthropic.types.Message, start: float) -> LLMResponse:
        """Build the LLMResponse; ``start`` is the monotonic call start."""
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
            logger=self._log,
        )
        return LLMResponse(
            content=text,
            input_tokens=plain_in + cache_create + cache_read,
            output_tokens=out,
            cost_usd=cost,
            duration_ms=int((time.monotonic() - start) * 1000),
            cache_creation_input_tokens=cache_create,
            cache_read_input_tokens=cache_read,
            truncated=(getattr(msg, "stop_reason", None) == "max_tokens"),
        )

    def _extract_text(self, msg: anthropic.types.Message) -> str:
        for block in msg.content:
            text = getattr(block, "text", None)
            if isinstance(text, str):
                return text
        return ""
