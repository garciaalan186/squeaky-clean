"""ResumeRunExecutor: wires the pipeline with cached-stage dep substitutes (G3)."""

from __future__ import annotations

from pathlib import Path

from squeaky_clean.application.dtos.eval_report_bundle import EvalReportBundle
from squeaky_clean.application.dtos.module_implementation import ModuleImplementation
from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.application.dtos.run_checkpoint import RunCheckpoint
from squeaky_clean.application.dtos.test_architecture import TestArchitecture
from squeaky_clean.application.use_cases.module_implementation_serializer import (
    ModuleImplementationSerializer,
)
from squeaky_clean.application.use_cases.parse_architecture_notation import (
    ParseArchitectureNotation,
)
from squeaky_clean.application.use_cases.resume_stub_factory import ResumeStubFactory
from squeaky_clean.application.use_cases.run_eval_dependencies import RunEvalDependencies
from squeaky_clean.application.use_cases.run_eval_pipeline import RunEvalPipeline
from squeaky_clean.application.use_cases.test_architecture_serializer import (
    TestArchitectureSerializer,
)
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec

_RESUMABLE_STAGES = frozenset({"icps_done", "integrated", "tested", "fixed"})


class ResumeRunExecutor:
    """Build a stubbed RunEvalDependencies bundle then run the pipeline."""

    def __init__(self, deps: RunEvalDependencies) -> None:
        self._deps: RunEvalDependencies = deps

    def run_full(
        self, problem: ProblemSpec, run_dir: Path,
    ) -> EvalReportBundle:
        """Restart the pipeline from scratch in the existing run_dir."""
        return RunEvalPipeline(self._deps).run(problem, run_dir)

    def resume_from(
        self, cp: RunCheckpoint, problem: ProblemSpec, run_dir: Path,
    ) -> EvalReportBundle:
        """Resume the pipeline using checkpoint state for completed stages."""
        if cp.stage not in _RESUMABLE_STAGES:
            return self.run_full(problem, run_dir)
        arch = self._load_architecture(cp)
        test_arch = self._load_test_arch(cp.test_architecture_path)
        sec_arch = self._load_test_arch(cp.security_test_architecture_path)
        impls = self._load_impls(cp)
        deps = ResumeStubFactory().build(
            self._deps, arch, test_arch, sec_arch, impls,
            prior_cost_usd=cp.cost_spent_usd,
        )
        return RunEvalPipeline(deps).run(problem, run_dir)

    def _load_architecture(self, cp: RunCheckpoint) -> ArchitectureSpec:
        if not cp.architecture_notation:
            raise ValueError("checkpoint missing architecture_notation")
        return ParseArchitectureNotation().parse(cp.architecture_notation)

    def _load_test_arch(self, path_str: str) -> TestArchitecture:
        if not path_str:
            return TestArchitecture(gherkin_scenarios=(), test_skeletons=())
        return TestArchitectureSerializer().deserialize(
            Path(path_str).read_text()
        )

    def _load_impls(
        self, cp: RunCheckpoint,
    ) -> tuple[ModuleImplementation, ...]:
        return ModuleImplementationSerializer().deserialize(
            Path(cp.module_implementations_path).read_text()
        )
