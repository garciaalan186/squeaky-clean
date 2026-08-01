"""TierUsage: one routing tier's accumulated LLM usage samples."""

from dataclasses import dataclass


@dataclass(frozen=True)
class TierUsage:
    """Read-side snapshot of one tier's usage from LLMUsageRecorder.

    ``cache_create_tokens``/``cache_read_tokens`` feed cache-savings
    analysis; ``durations_ms``/``costs_usd`` are per-call samples for
    percentile computation (G2).
    """

    cache_create_tokens: int
    cache_read_tokens: int
    durations_ms: tuple[int, ...]
    costs_usd: tuple[float, ...]
