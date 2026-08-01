"""ObligationRepairResult: residual gaps + aggregated repair usage."""

from dataclasses import dataclass

from squeaky_clean.application.generation.repair.fixer_stage import FixerStageResult


@dataclass(frozen=True)
class ObligationRepairResult:
    """Residual undischarged obligations + aggregated repair usage."""

    residual_gaps: int
    usage: FixerStageResult
