"""CompileGate: compile a project and drive fixer retries on compile errors."""

from dataclasses import dataclass
from pathlib import Path

from squeaky_clean.application.dtos.compile_result import CompileResult
from squeaky_clean.application.dtos.fix_request import FixRequest
from squeaky_clean.application.dtos.module_implementation import ModuleImplementation
from squeaky_clean.application.dtos.test_run_result import TestRunResult
from squeaky_clean.application.use_cases.fixer_stage import (
    FixerStage,
    FixerStageResult,
)
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.interfaces.project_compiler import ProjectCompiler


@dataclass(frozen=True)
class CompileGateRequest:
    """Inputs to one CompileGate run."""

    implementation: ModuleImplementation
    output_dir: Path
    max_passes: int
    architecture: ArchitectureSpec | None = None


@dataclass(frozen=True)
class CompileGateResult:
    """Outcome: residual compile-error count + aggregated fixer usage."""

    compile_errors: int
    fixer: FixerStageResult


class CompileGate:
    """Compile before tests; on failure, fix implicated source classes.

    A no-op (zero errors) when no compiler is wired for the language, so
    dynamically-typed targets simply skip the gate.
    """

    def __init__(
        self, compiler: ProjectCompiler | None, fixer_stage: FixerStage,
    ) -> None:
        self._compiler: ProjectCompiler | None = compiler
        self._fixer: FixerStage = fixer_stage

    def run(self, request: CompileGateRequest) -> CompileGateResult:
        """Compile, retry-fix up to ``max_passes``, return residual errors."""
        if self._compiler is None:
            return CompileGateResult(0, FixerStageResult(0, 0, 0, 0.0, 0, 0))
        agg = FixerStageResult(0, 0, 0, 0.0, 0, 0)
        result = self._compiler.compile(request.output_dir)
        for _ in range(max(0, request.max_passes)):
            if result.ok or not result.offending_stems:
                break
            stats = self._fixer.apply(
                self._fix_request(request, result), request.output_dir,
            )
            agg = agg.merge(stats)
            if stats.classes_fixed == 0:
                break
            result = self._compiler.compile(request.output_dir)
        return CompileGateResult(result.error_count, agg)

    @staticmethod
    def _fix_request(
        request: CompileGateRequest, result: CompileResult,
    ) -> FixRequest:
        return FixRequest(
            implementation=request.implementation,
            test_run_result=TestRunResult(
                0, result.error_count, 0, 0, result.raw_output),
            override_stems=result.offending_stems,
            architecture=request.architecture,
        )
