"""TestArchitectureStage: per-module oracle generation, functional + security."""

from __future__ import annotations

from dataclasses import replace

from squeaky_clean.application.evaluation.eval.run.run_eval_dependencies import RunEvalDependencies
from squeaky_clean.application.evaluation.eval.run.stages.stage_context import PipelineContext
from squeaky_clean.application.generation.architecture.architecture_merger import ArchitectureMerger
from squeaky_clean.application.generation.security.security_review_context import (
    SecurityReviewContext,
)
from squeaky_clean.application.generation.security.security_test_context import SecurityTestContext
from squeaky_clean.application.generation.testgen.test_architecture import TestArchitecture
from squeaky_clean.application.generation.testgen.test_architecture_context import (
    TestArchitectureContext,
)
from squeaky_clean.application.shared.mcda.per_module_criterion_filter import (
    filter_criteria_for_module,
)
from squeaky_clean.domain.value_objects.layer_type import LayerType


class TestArchitectureStage:
    """Merges per-module test architectures (+ security variant when enabled)."""

    def __init__(
        self, deps: RunEvalDependencies, merger: ArchitectureMerger,
    ) -> None:
        self._deps = deps
        self._merger = merger

    def run(self, ctx: PipelineContext) -> PipelineContext:
        arch = ctx.arch
        assert arch is not None
        filtered = 0
        per_module: list[TestArchitecture] = []
        for m in arch.modules:
            # rec 3: Infrastructure adapters need live infra — the developer
            # owns their integration tests. Skip generation for the layer.
            if m.layer is LayerType.INFRASTRUCTURE:
                continue
            kept = filter_criteria_for_module(ctx.problem.acceptance_criteria, m)
            # No criterion targets this module — invariants are emitted
            # deterministically; skip the LLM oracle for it.
            if not kept:
                filtered += len(ctx.problem.acceptance_criteria)
                continue
            filtered += len(ctx.problem.acceptance_criteria) - len(kept)
            per_module.append(self._deps.generate_test_architecture.execute(
                TestArchitectureContext(
                    module=m, problem=ctx.problem, architecture=arch,
                ),
            ))
        test_arch = self._merger.merge_test_architectures(per_module)
        sec_arch = (
            self._security_arch(ctx)
            if self._deps.run_config.enable_security_tests
            else TestArchitecture(gherkin_scenarios=(), test_skeletons=()))
        ctx.emitter.test_arch_done(test_arch, sec_arch)
        return replace(ctx,
            test_arch=test_arch, sec_arch=sec_arch,
            counters=replace(ctx.counters, test_criteria_filtered=filtered),
        )

    def _security_arch(self, ctx: PipelineContext) -> TestArchitecture:
        arch = ctx.arch
        assert arch is not None
        per_module: list[TestArchitecture] = []
        for m in arch.modules:
            review = self._deps.review_security.execute(
                SecurityReviewContext(module=m, problem=ctx.problem),
            )
            per_module.append(self._deps.generate_security_tests.execute(
                SecurityTestContext(
                    review=review, module=m, problem=ctx.problem,
                    architecture=arch,
                ),
            ))
        return self._merger.merge_test_architectures(per_module)
