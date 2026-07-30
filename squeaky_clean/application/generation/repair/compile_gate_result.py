"""CompileGateResult: residual compile-error count + aggregated fixer usage."""

from dataclasses import dataclass

from squeaky_clean.application.generation.repair.fixer_stage_result import FixerStageResult


@dataclass(frozen=True)
class CompileGateResult:
    """Outcome: residual compile-error count + aggregated fixer usage."""

    compile_errors: int
    fixer: FixerStageResult
