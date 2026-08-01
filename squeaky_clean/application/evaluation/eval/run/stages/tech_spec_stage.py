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
from squeaky_clean.application.generation.techspec.infrastructure_choice import (
    InfrastructureChoice,
)
from squeaky_clean.application.generation.techspec.select_infrastructure_choices import (
    select_infrastructure_choices,
)
from squeaky_clean.domain.interfaces.tech_spec_resolver import TechSpecResolver
from squeaky_clean.domain.interfaces.techspec.tech_spec_resolution_error import (
    TechSpecResolutionError,
)
from squeaky_clean.domain.value_objects.tech_spec import TechSpec
from squeaky_clean.domain.value_objects.tech_spec_target import TechSpecTarget


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
        specs = self._resolve_all(resolver, choices)
        self._orchestrator.register_tech_specs(specs)
        counters = replace(ctx.counters, infra_explicit=explicit_count,
                           infra_derived=derived_count, mcda_runs=derived_count)
        return replace(ctx, tech_specs={s.category: s for s in specs},
                       counters=counters)

    def _resolve_all(
        self, resolver: TechSpecResolver, choices: tuple[InfrastructureChoice, ...],
    ) -> tuple[TechSpec, ...]:
        """Resolve every choice; failure logs reasons, then fails the run (R6.8)."""
        targets = (
            TechSpecTarget(c.category, c.technology, c.version_pin)
            for c in choices
        )
        try:
            return tuple(resolver.resolve(t) for t in targets)
        except TechSpecResolutionError as exc:
            self._deps.run_logger.event(
                "tech_spec_resolution_failed",
                error=str(exc), reasons=list(exc.reasons),
            )
            raise
