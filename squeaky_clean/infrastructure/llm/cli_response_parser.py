"""CLIResponseParser: turn raw `claude -p --output-format json` output."""

import json

from squeaky_clean.domain.interfaces.llm_response import LLMResponse
from squeaky_clean.infrastructure.llm.llm_gateway_error import LLMGatewayError


class CLIResponseParser:
    """Parses the JSON emitted by `claude -p --output-format json`."""

    def parse(self, raw_stdout: str) -> LLMResponse:
        """Return an LLMResponse or raise LLMGatewayError on errors."""
        try:
            payload = json.loads(raw_stdout)
        except json.JSONDecodeError as exc:
            raise LLMGatewayError(f"invalid CLI JSON: {exc}") from exc
        if not isinstance(payload, dict):
            raise LLMGatewayError("CLI JSON was not an object")
        if payload.get("is_error") is True:
            raise LLMGatewayError(
                f"claude CLI returned error: {payload.get('result', '')}"
            )
        usage = payload.get("usage") or {}
        if not isinstance(usage, dict):
            raise LLMGatewayError("CLI usage field was not an object")
        cache_create = int(usage.get("cache_creation_input_tokens", 0) or 0)
        cache_read = int(usage.get("cache_read_input_tokens", 0) or 0)
        input_total = (
            int(usage.get("input_tokens", 0) or 0)
            + cache_create
            + cache_read
        )
        return LLMResponse(
            content=str(payload.get("result", "")),
            input_tokens=input_total,
            output_tokens=int(usage.get("output_tokens", 0) or 0),
            cost_usd=float(payload.get("total_cost_usd", 0.0) or 0.0),
            duration_ms=int(payload.get("duration_ms", 0) or 0),
            cache_creation_input_tokens=cache_create,
            cache_read_input_tokens=cache_read,
        )
