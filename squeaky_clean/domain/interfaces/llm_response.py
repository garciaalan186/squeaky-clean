"""LLMResponse DTO: the result of a completed LLMGateway call."""

from dataclasses import dataclass


@dataclass(frozen=True)
class LLMResponse:
    """Immutable response containing text, token counts, cost, and timing."""

    content: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    duration_ms: int
    cache_creation_input_tokens: int = 0
    cache_read_input_tokens: int = 0
    timed_out: bool = False
    cache_hit: bool = False
