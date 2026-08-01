"""TechSpecComposer: bridge producing an InstantiatedICPPrompt (H2)."""

from __future__ import annotations

from dataclasses import replace

from squeaky_clean.application.generation.emission.class_assignment import ClassAssignment
from squeaky_clean.application.generation.emission.class_assignment_formatter import (
    ClassAssignmentFormatter,
)
from squeaky_clean.application.generation.emission.instantiated_icp_prompt import (
    InstantiatedICPPrompt,
)
from squeaky_clean.application.generation.emission.load_agent_spec import LoadAgentSpec
from squeaky_clean.application.generation.techspec.composer_stats import ComposerStats
from squeaky_clean.application.generation.techspec.composition_failure import CompositionFailure
from squeaky_clean.application.generation.techspec.techspec_composer_manager_call import (
    TechSpecComposerManagerCall,
)
from squeaky_clean.application.generation.techspec.techspec_composer_validator import (
    validate_composition,
)
from squeaky_clean.domain.interfaces.llm_gateway import LLMGateway
from squeaky_clean.domain.interfaces.model_routing_policy import ModelRoutingPolicy
from squeaky_clean.domain.interfaces.run_logger import RunLogger
from squeaky_clean.domain.value_objects.model_tier import ModelTier
from squeaky_clean.domain.value_objects.tech_spec import TechSpec
from squeaky_clean.infrastructure.techspec.tech_spec_builder import TechSpecBuilder


class TechSpecComposer:
    """Bridge from (ClassAssignment, TechSpec) to a ready-to-dispatch prompt."""

    def __init__(
        self, gateway: LLMGateway, routing: ModelRoutingPolicy,
        *, loader: LoadAgentSpec, logger: RunLogger | None = None,
    ) -> None:
        self._loader = loader
        self._builder = TechSpecBuilder()
        self._manager = TechSpecComposerManagerCall(gateway, routing, logger=logger)
        self.stats: ComposerStats = ComposerStats()

    def compose(
        self, assignment: ClassAssignment, tech_spec: TechSpec,
    ) -> InstantiatedICPPrompt:
        """Render the Tier C prompt; escalate to Manager on validation failure."""
        sibs = frozenset(c.name for c in assignment.module.classes)
        errors = validate_composition(assignment.class_spec, tech_spec, sibs)
        active = tech_spec if not errors else self._reconcile(
            assignment, tech_spec, errors, sibs)
        return self._render(assignment, active)

    def _reconcile(
        self, assignment: ClassAssignment, tech_spec: TechSpec,
        errors: tuple[str, ...], siblings: frozenset[str],
    ) -> TechSpec:
        self._bump(validation_failures=1, manager_fallback_calls=1)
        proposal = self._manager.request_correction(
            CompositionFailure(assignment, tech_spec, errors),
        )
        if proposal is None:
            return tech_spec  # Manager declined; proceed with original spec
        try:
            corrected = self._builder.build(proposal)
        except (AttributeError, KeyError, TypeError, ValueError):
            return tech_spec  # malformed proposal; fall back gracefully
        residual = validate_composition(
            assignment.class_spec, corrected, siblings,
        )
        if residual:
            return tech_spec  # correction didn't fully clean; use original
        self._bump(manager_corrections_accepted=1)
        return corrected

    def _render(
        self, assignment: ClassAssignment, tech_spec: TechSpec,
    ) -> InstantiatedICPPrompt:
        rendered = replace(assignment, tech_spec=tech_spec)
        return InstantiatedICPPrompt(
            system_prompt=self._loader.load(assignment.emitter_spec_name),
            user_prompt=ClassAssignmentFormatter(assignment.toolkit).format(rendered),
            model_tier=ModelTier.ICP,
        )

    def _bump(self, **kwargs: int) -> None:
        self.stats = replace(self.stats, **{
            k: getattr(self.stats, k) + v for k, v in kwargs.items()
        })
