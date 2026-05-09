"""Tests for LLMUsageRecorder."""

from squeaky_clean.application.use_cases.llm_usage_recorder import LLMUsageRecorder
from squeaky_clean.domain.interfaces.llm_response import LLMResponse


def _resp(in_tok: int, out_tok: int, cost: float = 0.0, dur: int = 0) -> LLMResponse:
    return LLMResponse(
        content="",
        input_tokens=in_tok,
        output_tokens=out_tok,
        cost_usd=cost,
        duration_ms=dur,
    )


def test_fresh_recorder_returns_zero() -> None:
    rec = LLMUsageRecorder()
    assert rec.stats() == (0, 0, 0.0, 0)
    assert rec.stats("architect") == (0, 0, 0.0, 0)


def test_record_accumulates_per_label() -> None:
    rec = LLMUsageRecorder()
    rec.record(_resp(10, 5, 0.01, 100), "architect")
    rec.record(_resp(30, 15, 0.03, 200), "architect")
    rec.record(_resp(20, 8, 0.02, 150), "test_architect")
    assert rec.stats("architect") == (40, 20, 0.04, 300)
    assert rec.stats("test_architect") == (20, 8, 0.02, 150)
    t_in, t_out, t_cost, t_dur = rec.stats()
    assert t_in == 60
    assert t_out == 28
    assert abs(t_cost - 0.06) < 1e-9
    assert t_dur == 450


def test_unknown_label_returns_zero() -> None:
    rec = LLMUsageRecorder()
    rec.record(_resp(5, 3, 0.01, 50), "a")
    assert rec.stats("nonexistent") == (0, 0, 0.0, 0)
