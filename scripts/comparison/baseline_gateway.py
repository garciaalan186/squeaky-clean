"""BaselineLLMGateway: monolithic-call gateway for baseline comparisons.

Mirrors LLMGateway's `complete()` signature so the existing LLMRequest /
LLMResponse types flow through unchanged. The only differences are:

- No agent-tier routing; the gateway is constructed with a single fixed
  model and used for one-shot or retry-equipped completions.
- No prompt cache_control attached (we want the baseline to pay full
  per-call cost; cache savings are a Squeaky-side property).

VanillaOpusGateway is the first concrete implementation. Future "vanilla
Sonnet" / "vanilla Haiku" plug into the same interface so the
model-identity confounder can be teased apart later.
"""
from __future__ import annotations

import os
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass

import anthropic

from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.domain.interfaces.llm_response import LLMResponse
from squeaky_clean.infrastructure.llm.model_pricing import estimate_cost_usd

_DEFAULT_MAX_TOKENS = 8192
_DEFAULT_TIMEOUT = 480.0


class BaselineLLMGateway(ABC):
    """A monolithic-call gateway used in baseline comparisons."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Short identifier ('vanilla-opus', 'vanilla-sonnet', ...)."""

    @abstractmethod
    def complete(self, request: LLMRequest) -> LLMResponse:
        """Submit a single prompt; return the completion."""


@dataclass(frozen=True)
class VanillaOpusGateway(BaselineLLMGateway):
    """Direct-SDK Opus baseline. No prompt-cache, no agent-tier routing."""

    model: str = "claude-opus-4-7"
    max_tokens: int = _DEFAULT_MAX_TOKENS
    timeout: float = _DEFAULT_TIMEOUT

    @property
    def name(self) -> str:
        return "vanilla-opus"

    def complete(self, request: LLMRequest) -> LLMResponse:
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY not set")
        client = anthropic.Anthropic(api_key=api_key, timeout=self.timeout)
        start = time.monotonic()
        kwargs: dict = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "system": request.system_prompt,
            "messages": [{"role": "user", "content": request.user_prompt}],
        }
        # Opus 4.7 deprecated temperature; only pass for older models.
        if not self.model.startswith("claude-opus-4-7"):
            kwargs["temperature"] = (
                request.temperature if request.temperature is not None else 0.0
            )
        msg = client.messages.create(**kwargs)
        text = ""
        for block in msg.content:
            if hasattr(block, "text") and isinstance(block.text, str):
                text = block.text
                break
        usage = msg.usage
        cost = estimate_cost_usd(
            model=str(msg.model),
            input_tokens=int(usage.input_tokens),
            output_tokens=int(usage.output_tokens),
            cache_creation_tokens=0,
            cache_read_tokens=0,
        )
        return LLMResponse(
            content=text,
            input_tokens=int(usage.input_tokens),
            output_tokens=int(usage.output_tokens),
            cost_usd=cost,
            duration_ms=int((time.monotonic() - start) * 1000),
        )
