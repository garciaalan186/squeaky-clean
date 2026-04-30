"""Tests for PercentileSummaryRenderer (G2)."""

from __future__ import annotations

from squeaky_clean.application.use_cases.llm_usage_recorder import LLMUsageRecorder
from squeaky_clean.application.use_cases.percentile_summary_renderer import (
    PercentileSummaryRenderer,
)
from squeaky_clean.domain.interfaces.llm_response import LLMResponse


def _resp(duration_ms: int, cost_usd: float) -> LLMResponse:
    return LLMResponse(
        content="x", input_tokens=10, output_tokens=10,
        cost_usd=cost_usd, duration_ms=duration_ms,
    )


def test_empty_recorder_renders_empty() -> None:
    rec = LLMUsageRecorder()
    out = PercentileSummaryRenderer().render(rec)
    assert out == ""


def test_single_tier_percentiles() -> None:
    rec = LLMUsageRecorder()
    for d in (100, 200, 300, 400, 500, 600, 700, 800, 900, 1000):
        rec.record(_resp(d, 0.001 * d), label="icp")
    out = PercentileSummaryRenderer().render(rec)
    assert "Latency / cost percentiles" in out
    assert "Icp" in out
    assert "500ms" in out  # p50 = sample[4] = 500
    assert "900ms" in out  # p95 = sample[8] = 900
    assert "$0.5000" in out  # p50 cost
    assert "$0.9000" in out  # p95 cost


def test_no_data_tier_shows_na() -> None:
    rec = LLMUsageRecorder()
    rec.record(_resp(100, 0.01), label="architect")
    out = PercentileSummaryRenderer().render(rec)
    assert "Architect" in out
    assert "Manager" in out
    # Manager had no data → n/a
    manager_line = [ln for ln in out.split("\n") if "Manager" in ln][0]
    assert "n/a" in manager_line
