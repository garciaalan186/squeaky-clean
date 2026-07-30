"""Tests for FixerStageResult (R2.4 extraction)."""

from squeaky_clean.application.use_cases.fixer_stage_result import FixerStageResult


def test_merge_sums_all_fields() -> None:
    a = FixerStageResult(1, 10, 20, 0.5, 100, 1)
    b = FixerStageResult(2, 5, 5, 0.25, 50, 1)
    m = a.merge(b)
    assert (m.classes_fixed, m.input_tokens, m.output_tokens) == (3, 15, 25)
    assert m.cost_usd == 0.75 and m.duration_ms == 150 and m.passes == 2
