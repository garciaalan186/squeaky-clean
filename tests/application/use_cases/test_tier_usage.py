"""Tests for TierUsage: the per-tier usage snapshot value object."""

from squeaky_clean.application.shared.gateways.llm_usage_recorder import LLMUsageRecorder
from squeaky_clean.application.shared.gateways.tier_usage import TierUsage
from squeaky_clean.domain.interfaces.llm_response import LLMResponse


def _resp(duration_ms: int, cost: float) -> LLMResponse:
    return LLMResponse(
        content="ok", input_tokens=10, output_tokens=5, cost_usd=cost,
        duration_ms=duration_ms, cache_creation_input_tokens=7,
        cache_read_input_tokens=3,
    )


def test_recorder_snapshots_one_tier() -> None:
    rec = LLMUsageRecorder()
    rec.record(_resp(100, 0.01), "icp")
    rec.record(_resp(200, 0.02), "security_icp")  # same routing tier
    usage = rec.tier_stats("icp")
    assert usage == TierUsage(
        cache_create_tokens=14, cache_read_tokens=6,
        durations_ms=(100, 200), costs_usd=(0.01, 0.02),
    )


def test_unknown_tier_yields_empty_snapshot() -> None:
    usage = LLMUsageRecorder().tier_stats("architect")
    assert usage == TierUsage(
        cache_create_tokens=0, cache_read_tokens=0,
        durations_ms=(), costs_usd=(),
    )
