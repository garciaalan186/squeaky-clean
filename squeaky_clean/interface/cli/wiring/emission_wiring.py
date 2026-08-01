"""EmissionWiring: per-problem toolkit, adapters, and module orchestrator."""

from pathlib import Path

from squeaky_clean.application.generation.emission.assign_patterns import AssignPatterns
from squeaky_clean.application.generation.emission.implement_class import ImplementClass
from squeaky_clean.application.generation.emission.orchestrate_module import OrchestrateModule
from squeaky_clean.application.generation.emission.parsers.parse_implemented_class import (
    ParseImplementedClass,
)
from squeaky_clean.application.generation.techspec.techspec_composer import TechSpecComposer
from squeaky_clean.application.shared.language.language_toolkit_factory import (
    LanguageToolkitFactory,
)
from squeaky_clean.application.shared.problem.problem_spec import ProblemSpec
from squeaky_clean.domain.value_objects.model_tier import ModelTier
from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.infrastructure.llm.model_router import ModelRouter
from squeaky_clean.interface.cli.language_adapter_selector import LanguageAdapterSelector
from squeaky_clean.interface.cli.wiring.emission_bundle import EmissionBundle
from squeaky_clean.interface.cli.wiring.wiring_context import WiringContext


class EmissionWiring:
    """Wires the language-specific emission stack for one problem."""

    def __init__(self, ctx: WiringContext) -> None:
        self._ctx: WiringContext = ctx

    def wire(self, problem: ProblemSpec) -> EmissionBundle:
        """Return the toolkit/adapters/orchestrator bundle for ``problem``."""
        ctx = self._ctx
        rc = ctx.run_config
        toolkit = LanguageToolkitFactory().for_language(problem.target_language)
        adapters = LanguageAdapterSelector(ctx.logger).select(toolkit, ctx.fs)
        assigner = AssignPatterns(
            toolkit, Path(""),
            infrastructure_mode=rc.infrastructure_mode,
        )
        composer = (
            TechSpecComposer(ctx.gateway, ctx.router, loader=ctx.loader)
            if rc.infrastructure_mode == "auto" else None
        )
        parser = ParseImplementedClass(adapters.parser)
        orchestrator = OrchestrateModule(
            ImplementClass(
                ctx.gateway,
                self._icp_router(ctx.router, problem.target_language),
                rc, composer=composer, parser=parser, loader=ctx.loader,
            ),
            assigner,
        )
        return EmissionBundle(
            toolkit=toolkit, adapters=adapters, orchestrate_module=orchestrator,
        )

    @staticmethod
    def _icp_router(base: ModelRouter, lang: TargetLanguage) -> ModelRouter:
        if lang is not TargetLanguage.JAVA:
            return base
        m = {t: base.route(t) for t in ModelTier}
        m[ModelTier.ICP] = m[ModelTier.MANAGER]
        return ModelRouter(m)
