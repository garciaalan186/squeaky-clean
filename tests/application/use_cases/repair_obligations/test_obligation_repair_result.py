"""Tests for the ObligationRepairResult DTO."""

from squeaky_clean.application.generation.repair.fixer_stage import FixerStageResult
from squeaky_clean.application.generation.repair.obligations.obligation_repair_result import (
    ObligationRepairResult,
)


def test_result_carries_residual_gaps_and_usage() -> None:
    usage = FixerStageResult(1, 10, 20, 0.5, 100, 1)
    result = ObligationRepairResult(residual_gaps=3, usage=usage)
    assert result.residual_gaps == 3
    assert result.usage is usage
