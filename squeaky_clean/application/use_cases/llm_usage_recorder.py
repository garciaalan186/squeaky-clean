"""LLMUsageRecorder: accumulates tokens, cost, duration per agent label."""

from collections import defaultdict

from squeaky_clean.domain.interfaces.llm_response import LLMResponse

_EMPTY: list[float] = [0.0, 0.0, 0.0, 0.0]
_LABEL_TO_TIER: dict[str, str] = {
    "architect": "architect",
    "test_architect": "manager",
    "security_architect": "manager",
    "manager": "manager",
    "icp": "icp",
    "security_icp": "icp",
    "fixer": "fixer",
}


class LLMUsageRecorder:
    """Mutable accumulator bucketed by agent label.

    Each bucket stores ``[input_tokens, output_tokens, cost_usd, duration_ms]``.
    ``stats(label)`` returns one bucket; ``stats(None)`` returns the grand total.
    Side counters track cache hits/misses, timeouts, and cache token totals,
    and per-tier ``(create, read, model)`` triples for cache savings analysis.
    """

    def __init__(self) -> None:
        self._buckets: dict[str, list[float]] = defaultdict(
            lambda: [0.0, 0.0, 0.0, 0.0]
        )
        self._cache_hits: int = 0
        self._cache_misses: int = 0
        self._cache_create_tokens: int = 0
        self._cache_read_tokens: int = 0
        self._timeouts: int = 0
        self._tier_create: dict[str, int] = defaultdict(int)
        self._tier_read: dict[str, int] = defaultdict(int)
        # G2: per-call samples for percentile computation. Keyed by tier.
        self._tier_durations_ms: dict[str, list[int]] = defaultdict(list)
        self._tier_costs_usd: dict[str, list[float]] = defaultdict(list)

    def record(self, response: LLMResponse, label: str) -> None:
        """Accumulate one LLMResponse under ``label``."""
        b = self._buckets[label]
        b[0] += response.input_tokens
        b[1] += response.output_tokens
        b[2] += response.cost_usd
        b[3] += response.duration_ms
        if response.cache_hit:
            self._cache_hits += 1
        else:
            self._cache_misses += 1
        self._cache_create_tokens += response.cache_creation_input_tokens
        self._cache_read_tokens += response.cache_read_input_tokens
        tier = _LABEL_TO_TIER.get(label, label)
        self._tier_create[tier] += response.cache_creation_input_tokens
        self._tier_read[tier] += response.cache_read_input_tokens
        self._tier_durations_ms[tier].append(response.duration_ms)
        self._tier_costs_usd[tier].append(response.cost_usd)
        if response.timed_out:
            self._timeouts += 1

    def tier_samples(
        self, tier: str,
    ) -> tuple[tuple[int, ...], tuple[float, ...]]:
        """Return per-call ``(durations_ms, costs_usd)`` samples for a tier."""
        return (
            tuple(self._tier_durations_ms.get(tier, [])),
            tuple(self._tier_costs_usd.get(tier, [])),
        )

    def stats(self, label: str | None = None) -> tuple[int, int, float, int]:
        """Return ``(in_tok, out_tok, cost_usd, duration_ms)``."""
        if label is not None:
            b = self._buckets.get(label, _EMPTY)
            return (int(b[0]), int(b[1]), b[2], int(b[3]))
        return (
            int(sum(b[0] for b in self._buckets.values())),
            int(sum(b[1] for b in self._buckets.values())),
            sum(b[2] for b in self._buckets.values()),
            int(sum(b[3] for b in self._buckets.values())),
        )

    def cache_stats(self) -> tuple[int, int, int, int]:
        """Return ``(hits, misses, cache_create_tokens, cache_read_tokens)``."""
        return (
            self._cache_hits,
            self._cache_misses,
            self._cache_create_tokens,
            self._cache_read_tokens,
        )

    def tier_cache_stats(self, tier: str) -> tuple[int, int]:
        """Return ``(cache_create_tokens, cache_read_tokens)`` for ``tier``."""
        return (self._tier_create.get(tier, 0), self._tier_read.get(tier, 0))

    def timeout_count(self) -> int:
        """Number of LLMResponse instances flagged as timed out."""
        return self._timeouts
