"""PipelineOutputs: collected pipeline results used to build MetricsInputs."""

from dataclasses import dataclass

from squeaky_clean.application.dtos.composer_stats import ComposerStats
from squeaky_clean.application.dtos.module_implementation import ModuleImplementation
from squeaky_clean.application.dtos.test_architecture import TestArchitecture
from squeaky_clean.application.dtos.test_run_result import TestRunResult
from squeaky_clean.application.dtos.validation_report import ValidationReport
from squeaky_clean.application.use_cases.fixer_stage import FixerStageResult


@dataclass(frozen=True)
class PipelineOutputs:
    """Frozen snapshot of one pipeline run; consumed by MetricsInputsAssembler."""

    implementation: ModuleImplementation
    test_run: TestRunResult
    validation: ValidationReport
    func_run: TestRunResult | None
    security_architecture: TestArchitecture
    fix_stats: FixerStageResult
    composer_stats: ComposerStats = ComposerStats()
