"""EmissionStage: fan ICPs out over the architecture; merge module outputs."""

from __future__ import annotations

from dataclasses import replace

from squeaky_clean.application.evaluation.eval.run.stages.stage_context import PipelineContext
from squeaky_clean.application.generation.architecture.architecture_merger import ArchitectureMerger
from squeaky_clean.application.generation.architecture.orchestrate_architecture import (
    OrchestrateArchitecture,
)


class EmissionStage:
    """Runs the emitter fleet per module and flattens the implementations."""

    def __init__(
        self, orchestrator: OrchestrateArchitecture, merger: ArchitectureMerger,
    ) -> None:
        self._orchestrator = orchestrator
        self._merger = merger

    def run(self, ctx: PipelineContext) -> PipelineContext:
        arch = ctx.arch
        assert arch is not None
        module_impls = self._orchestrator.execute(arch)
        ctx.emitter.icps_done(module_impls)
        impl = self._merger.merge_implementations(arch, module_impls)
        return replace(ctx, module_impls=module_impls, impl=impl)
