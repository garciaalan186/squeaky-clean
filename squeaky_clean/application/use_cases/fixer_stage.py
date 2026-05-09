"""FixerStage: runs FixFailingClasses and rewrites repaired files to disk."""

from dataclasses import dataclass
from pathlib import Path

from squeaky_clean.application.dtos.fix_request import FixRequest
from squeaky_clean.application.dtos.module_implementation import ModuleImplementation
from squeaky_clean.application.dtos.test_run_result import TestRunResult
from squeaky_clean.application.use_cases.fix_failing_classes import FixFailingClasses
from squeaky_clean.application.use_cases.integration_file_writer import IntegrationFileWriter
from squeaky_clean.domain.interfaces.project_file_system import ProjectFileSystem


@dataclass(frozen=True)
class FixerStageResult:
    """Aggregated outcome of one (or many) fixer-stage invocation(s)."""

    classes_fixed: int
    input_tokens: int
    output_tokens: int
    cost_usd: float
    duration_ms: int
    passes: int = 0

    def merge(self, other: "FixerStageResult") -> "FixerStageResult":
        """Sum two FixerStageResults; use for multi-pass aggregation."""
        return FixerStageResult(
            classes_fixed=self.classes_fixed + other.classes_fixed,
            input_tokens=self.input_tokens + other.input_tokens,
            output_tokens=self.output_tokens + other.output_tokens,
            cost_usd=self.cost_usd + other.cost_usd,
            duration_ms=self.duration_ms + other.duration_ms,
            passes=self.passes + other.passes,
        )


class FixerStage:
    """Orchestrates: run fixer, rewrite files, return stats. No-op on skip."""

    def __init__(
        self,
        fixer: FixFailingClasses | None,
        file_system: ProjectFileSystem | None,
    ) -> None:
        self._fixer: FixFailingClasses | None = fixer
        self._fs: ProjectFileSystem | None = file_system

    def apply(
        self, request: FixRequest, output_dir: Path,
    ) -> FixerStageResult:
        """Dispatch the fixer if wired in, rewrite repaired files, return stats."""
        if self._fixer is None or self._fs is None:
            return self._empty()
        if request.test_run_result.failed == 0 and request.test_run_result.errors == 0:
            return self._empty()
        result = self._fixer.execute(request)
        if not result.fixed_classes:
            return self._empty()
        writer = IntegrationFileWriter(self._fs)
        for cls in result.fixed_classes:
            writer.write_class(cls, output_dir)
        return FixerStageResult(
            classes_fixed=len(result.fixed_classes),
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            cost_usd=result.cost_usd,
            duration_ms=result.duration_ms,
            passes=1,
        )

    def _empty(self) -> FixerStageResult:
        return FixerStageResult(0, 0, 0, 0.0, 0, 0)

    @staticmethod
    def requested(
        impl: ModuleImplementation, test_run: TestRunResult,
    ) -> FixRequest:
        """Convenience builder to match pipeline call site ergonomics."""
        return FixRequest(implementation=impl, test_run_result=test_run)
