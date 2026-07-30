"""Tests for CompileGateResult (R2.4 extraction)."""

from squeaky_clean.application.generation.repair.compile_gate_result import CompileGateResult
from squeaky_clean.application.generation.repair.fixer_stage_result import FixerStageResult


def test_holds_error_count_and_fixer() -> None:
    r = CompileGateResult(3, FixerStageResult(0, 0, 0, 0.0, 0, 0))
    assert r.compile_errors == 3 and r.fixer.classes_fixed == 0
