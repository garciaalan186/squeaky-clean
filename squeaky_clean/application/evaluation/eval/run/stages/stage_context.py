"""PipelineContext: the frozen, typed state threaded between stages (R6.2)."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from squeaky_clean.application.evaluation.eval.run.stages.stage_counters import StageCounters
from squeaky_clean.application.shared.problem.problem_spec import ProblemSpec

if TYPE_CHECKING:  # collaborator types only; avoids import cycles at runtime
    from squeaky_clean.application.evaluation.eval.resume.checkpoint_emitter import (
        CheckpointEmitter,
    )
    from squeaky_clean.application.generation.emission.module_implementation import (
        ModuleImplementation,
    )
    from squeaky_clean.application.generation.repair.fixer_stage import (
        FixerStageResult,
    )
    from squeaky_clean.application.generation.testgen.test_architecture import (
        TestArchitecture,
    )
    from squeaky_clean.application.generation.validation.validation_report import (
        ValidationReport,
    )
    from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
    from squeaky_clean.domain.interfaces.lifecycle_log import LifecycleLog
    from squeaky_clean.domain.value_objects.tech_spec import TechSpec
    from squeaky_clean.domain.value_objects.test_run_result import TestRunResult


@dataclass(frozen=True)
class PipelineContext:
    """Accumulates typed per-stage results; each stage returns a replace()d copy.

    Deliberately NOT another 106-field bag: run-scoped inputs + one optional
    slot per stage RESULT + the counters value. Stages return typed copies
    via ``dataclasses.replace``; nothing mutates another stage's output.
    """

    problem: ProblemSpec
    output_dir: Path
    emitter: CheckpointEmitter
    lifecycle: LifecycleLog
    counters: StageCounters = field(default_factory=StageCounters)
    arch: ArchitectureSpec | None = None
    test_arch: TestArchitecture | None = None
    sec_arch: TestArchitecture | None = None
    tech_specs: dict[str, TechSpec] = field(default_factory=dict)
    module_impls: tuple[ModuleImplementation, ...] = ()
    impl: ModuleImplementation | None = None
    validation: ValidationReport | None = None
    compile_errors: int = 0
    test_run: TestRunResult | None = None
    func_run: TestRunResult | None = None
    fix_stats: FixerStageResult | None = None
