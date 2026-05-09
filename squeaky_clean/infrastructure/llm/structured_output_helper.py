"""StructuredOutputHelper: invoke an SDK call constrained to a JSON schema.

Wraps Anthropic's tool-use API as a way to coerce the model into emitting
a JSON object matching a declared schema. Returns the parsed dict on
success, or None if the model emitted text instead of a tool_use block.
"""

from __future__ import annotations

import os
import time
from typing import cast

import anthropic

from squeaky_clean.domain.interfaces.llm_response import LLMResponse
from squeaky_clean.infrastructure.llm.llm_gateway_error import LLMGatewayError
from squeaky_clean.infrastructure.llm.model_pricing import estimate_cost_usd

_DEFAULT_TIMEOUT: float = 240.0
_DEFAULT_MAX_TOKENS: int = 4096


class StructuredOutputHelper:
    """Invoke `messages.create` with a single tool whose schema is the contract."""

    def __init__(self, api_key: str | None = None) -> None:
        key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        if not key:
            raise LLMGatewayError("ANTHROPIC_API_KEY not set")
        self._client: anthropic.Anthropic = anthropic.Anthropic(
            api_key=key, timeout=_DEFAULT_TIMEOUT,
        )

    def call(
        self,
        model: str,
        system_prompt: str,
        user_prompt: str,
        tool_name: str,
        input_schema: dict[str, object],
    ) -> tuple[dict[str, object] | None, LLMResponse]:
        """Return (parsed_tool_input or None, raw LLMResponse)."""
        start = time.monotonic()
        msg = self._client.messages.create(
            model=model,
            max_tokens=_DEFAULT_MAX_TOKENS,
            system=[{
                "type": "text", "text": system_prompt,
                "cache_control": {"type": "ephemeral"},
            }],
            messages=[{"role": "user", "content": user_prompt}],
            tools=[{
                "name": tool_name,
                "description": f"Emit a structured {tool_name} payload.",
                "input_schema": input_schema,
            }],
            tool_choice={"type": "tool", "name": tool_name},
        )
        usage = msg.usage
        cache_create = int(getattr(usage, "cache_creation_input_tokens", 0) or 0)
        cache_read = int(getattr(usage, "cache_read_input_tokens", 0) or 0)
        plain_in = int(usage.input_tokens)
        out = int(usage.output_tokens)
        cost = estimate_cost_usd(
            model=str(msg.model),
            input_tokens=plain_in, output_tokens=out,
            cache_creation_tokens=cache_create, cache_read_tokens=cache_read,
        )
        response = LLMResponse(
            content="", input_tokens=plain_in + cache_create + cache_read,
            output_tokens=out, cost_usd=cost,
            duration_ms=int((time.monotonic() - start) * 1000),
            cache_creation_input_tokens=cache_create,
            cache_read_input_tokens=cache_read,
        )
        for block in msg.content:
            if getattr(block, "type", None) == "tool_use":
                inp = getattr(block, "input", None)
                if isinstance(inp, dict):
                    return cast(dict[str, object], dict(inp)), response
        return None, response
