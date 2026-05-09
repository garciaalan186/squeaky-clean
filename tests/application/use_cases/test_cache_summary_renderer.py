"""Unit tests for CacheSummaryRenderer."""

from squeaky_clean.application.dtos.eval_metrics import EvalMetrics
from squeaky_clean.application.use_cases.cache_summary_renderer import CacheSummaryRenderer


def test_renders_zero_activity_message() -> None:
    out = "\n".join(CacheSummaryRenderer().render(EvalMetrics.empty()))
    assert "## Cache" in out
    assert "No prompt-cache activity" in out


def test_renders_table_when_tokens_present() -> None:
    m = EvalMetrics.empty()
    m.cache_creation_input_tokens = 1_200
    m.cache_read_input_tokens = 4_800
    m.cache_create_architect_tokens = 1_200
    m.cache_read_architect_tokens = 4_800
    m.cache_hit_ratio_architect = 0.8
    m.cache_savings_architect_usd = 0.018
    m.cache_savings_usd = 0.018
    out = "\n".join(CacheSummaryRenderer().render(m))
    assert "## Cache" in out
    assert "Cache create toks" in out
    assert "1,200" in out
    assert "4,800" in out
    assert "80.0%" in out
    assert "$0.018" in out
    assert "**Total**" in out


def test_per_tier_zero_rows_show_n_a() -> None:
    m = EvalMetrics.empty()
    m.cache_creation_input_tokens = 100
    m.cache_read_input_tokens = 0
    m.cache_create_architect_tokens = 100
    m.cache_savings_usd = -0.001
    out = "\n".join(CacheSummaryRenderer().render(m))
    # Manager / icp / fixer rows should show n/a since no tokens for them.
    assert "n/a" in out
