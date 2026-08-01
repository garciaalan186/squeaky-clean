"""TechSpecStage: H1+H3 — resolve TechSpecs (explicit + MCDA-derived)."""

from __future__ import annotations

from dataclasses import replace

from squeaky_clean.application.evaluation.eval.run.run_eval_dependencies import RunEvalDependencies
from squeaky_clean.application.evaluation.eval.run.stages.stage_context import PipelineContext
from squeaky_clean.application.generation.architecture.orchestrate_architecture import (
    OrchestrateArchitecture,
)
from squeaky_clean.application.generation.techspec.derive_required_categories import (
    derive_required_categories,
)
from squeaky_clean.application.generation.techspec.select_infrastructure_choices import (
    select_infrastructure_choices,
)


class TechSpecStage:
    """Resolves infrastructure TechSpecs and registers them for emission."""

    def __init__(
        self, deps: RunEvalDependencies, orchestrator: OrchestrateArchitecture,
    ) -> None:
        self._deps = deps
        self._orchestrator = orchestrator

    def run(self, ctx: PipelineContext) -> PipelineContext:
        if self._deps.run_config.infrastructure_mode != "auto":
            return ctx
        resolver = self._deps.tech_spec_resolver
        if resolver is None:
            return ctx
        arch = ctx.arch
        assert arch is not None
        infer = self._deps.run_config.infer_infrastructure
        explicit_count = len(ctx.problem.infrastructure_choices)
        required = derive_required_categories(arch) if infer else frozenset()
        choices = select_infrastructure_choices(
            ctx.problem, required, infer,
            self._deps.infrastructure_choice_architect,
        ) if (infer or ctx.problem.infrastructure_choices) else ()
        if not choices:
            return ctx
        derived_count = max(0, len(choices) - explicit_count)
        specs = tuple(
            resolver.resolve(c.category, c.technology, c.version_pin)
            for c in choices
        )
        self._orchestrator.register_tech_specs(specs)
        return replace(ctx,
            tech_specs={s.category: s for s in specs},
            counters=replace(ctx.counters,
                infra_explicit=explicit_count,
                infra_derived=derived_count,
                mcda_runs=derived_count,
            ),
        )
