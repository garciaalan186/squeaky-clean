"""TechSpecComposer: bridge producing an InstantiatedICPPrompt (H2)."""

from __future__ import annotations

from dataclasses import replace

from squeaky_clean.application.dtos.class_assignment import ClassAssignment
from squeaky_clean.application.dtos.composer_stats import ComposerStats
from squeaky_clean.application.dtos.instantiated_icp_prompt import InstantiatedICPPrompt
from squeaky_clean.application.dtos.tech_spec import TechSpec
from squeaky_clean.application.use_cases.class_assignment_formatter import (
    ClassAssignmentFormatter,
)
from squeaky_clean.application.use_cases.load_agent_spec import LoadAgentSpec
from squeaky_clean.application.use_cases.techspec_composer_manager_call import (
    TechSpecComposerManagerCall,
)
from squeaky_clean.application.use_cases.techspec_composer_validator import (
    validate_composition,
)
from squeaky_clean.domain.interfaces.llm_gateway import LLMGateway
from squeaky_clean.domain.value_objects.model_tier import ModelTier
from squeaky_clean.infrastructure.techspec.tech_spec_builder import TechSpecBuilder


class TechSpecComposer:
    """Bridge from (ClassAssignment, TechSpec) to a ready-to-dispatch prompt."""

    def __init__(
        self, gateway: LLMGateway, loader: LoadAgentSpec | None = None,
    ) -> None:
        self._loader = loader or LoadAgentSpec()
        self._builder = TechSpecBuilder()
        self._manager = TechSpecComposerManagerCall(gateway)
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
        proposal = self._manager.request_correction(assignment, tech_spec, errors)
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
            system_prompt=self._loader.load(assignment.icp_spec_name),
            user_prompt=ClassAssignmentFormatter(assignment.toolkit).format(rendered),
            model_tier=ModelTier.ICP,
        )

    def _bump(self, **kwargs: int) -> None:
        self.stats = replace(self.stats, **{
            k: getattr(self.stats, k) + v for k, v in kwargs.items()
        })
