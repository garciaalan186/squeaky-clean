"""PipelineOutputs: collected pipeline results used to build MetricsInputs."""

from dataclasses import dataclass

from squeaky_clean.application.generation.emission.module_implementation import ModuleImplementation
from squeaky_clean.application.generation.repair.fixer_stage import FixerStageResult
from squeaky_clean.application.generation.techspec.composer_stats import ComposerStats
from squeaky_clean.application.generation.testgen.test_architecture import TestArchitecture
from squeaky_clean.application.generation.validation.validation_report import ValidationReport
from squeaky_clean.domain.value_objects.test_run_result import TestRunResult


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
    wall_clock_ms: int = 0
