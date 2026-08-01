"""ResumeRunExecutor: wires the pipeline with cached-stage dep substitutes (G3)."""

from __future__ import annotations

from pathlib import Path

from squeaky_clean.application.evaluation.eval.resume.resume_stub_factory import ResumeStubFactory
from squeaky_clean.application.evaluation.eval.resume.run_checkpoint import RunCheckpoint
from squeaky_clean.application.evaluation.eval.run.eval_report_bundle import EvalReportBundle
from squeaky_clean.application.evaluation.eval.run.run_eval_dependencies import RunEvalDependencies
from squeaky_clean.application.evaluation.eval.run.run_eval_pipeline import RunEvalPipeline
from squeaky_clean.application.generation.emission.module_implementation import ModuleImplementation
from squeaky_clean.application.generation.notation.module_implementation_serializer import (
    ModuleImplementationSerializer,
)
from squeaky_clean.application.generation.notation.parse_architecture_notation import (
    ParseArchitectureNotation,
)
from squeaky_clean.application.generation.testgen.test_architecture import TestArchitecture
from squeaky_clean.application.generation.testgen.test_architecture_serializer import (
    TestArchitectureSerializer,
)
from squeaky_clean.application.shared.problem.problem_spec import ProblemSpec
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec

_RESUMABLE_STAGES = frozenset({"icps_done", "integrated", "tested", "fixed"})


class ResumeRunExecutor:
    """Run the pipeline for one checkpoint, stubbing already-completed stages."""

    def __init__(
        self, deps: RunEvalDependencies, cp: RunCheckpoint | None = None,
    ) -> None:
        self._deps: RunEvalDependencies = deps
        self._cp: RunCheckpoint | None = cp

    def resume(self, problem: ProblemSpec, run_dir: Path) -> EvalReportBundle:
        """Resume from the held checkpoint; restart from scratch without one."""
        cp = self._cp
        if cp is None or cp.stage not in _RESUMABLE_STAGES:
            return RunEvalPipeline(self._deps).run(problem, run_dir)
        deps = (
            ResumeStubFactory(self._deps, self._load_architecture(cp))
            .with_test_archs(
                self._load_test_arch(cp.test_architecture_path),
                self._load_test_arch(cp.security_test_architecture_path),
            )
            .with_impls(self._load_impls(cp))
            .build(cp.cost_spent_usd)
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
