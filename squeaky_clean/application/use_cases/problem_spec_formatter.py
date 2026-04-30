"""ProblemSpecFormatter: render a ProblemSpec into a user-prompt string."""

from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.application.use_cases.contract_registry import ContractRegistry
from squeaky_clean.application.use_cases.contract_section_renderer import (
    ContractSectionRenderer,
)
from squeaky_clean.application.use_cases.convention_to_invariant import (
    ConventionToInvariant,
)


class ProblemSpecFormatter:
    """Renders a ProblemSpec into the user-prompt body for an architect."""

    def __init__(self, registry: ContractRegistry | None = None) -> None:
        self._conv: ConventionToInvariant = ConventionToInvariant()
        reg = registry if registry is not None else ContractRegistry()
        self._contracts: ContractSectionRenderer = ContractSectionRenderer(reg)

    def format(self, problem: ProblemSpec) -> str:
        """Return a compact plain-text description of the problem."""
        lines: list[str] = [
            f"ProblemId: {problem.id}",
            f"TargetLanguage: {problem.target_language.value}",
            f"Description: {problem.description}",
            "AcceptanceCriteria:",
        ]
        for crit in problem.acceptance_criteria:
            lines.append(f"  - {crit}")
        lines.append("RequiredPatterns: " + ", ".join(problem.required_patterns))
        lines.append(
            "BoundedContexts: " + ", ".join(problem.required_bounded_contexts)
        )
        self._render_semantics(lines, problem)
        self._contracts.render(lines, problem)
        lines.append("")
        lines.append(
            "Emit one §Notation MODULE block describing the design. "
            "Output notation ONLY — no markdown fences, no prose."
        )
        return "\n".join(lines)

    def _render_semantics(
        self, lines: list[str], problem: ProblemSpec,
    ) -> None:
        """Append optional DomainConventions / QuerySemantics / etc. sections."""
        if problem.domain_conventions:
            lines.append("DomainConventions:")
            for tag in problem.domain_conventions:
                lines.append(f"  - {tag} → \"{self._conv.lookup(tag)}\"")
        if problem.query_semantics:
            lines.append("QuerySemantics:")
            for q in problem.query_semantics:
                lines.append(f"  - {q.use_case}: {q.shape}")
        if problem.entity_lifecycle:
            lines.append("EntityLifecycle:")
            for el in problem.entity_lifecycle:
                txt = ", ".join(
                    f"{t.from_state} → {t.to_state} ({t.trigger})"
                    for t in el.transitions
                )
                lines.append(f"  - {el.entity}: {txt}")
        if problem.data_classification:
            lines.append("DataClassification:")
            for d in problem.data_classification:
                lines.append(f"  - {d.field_ref}: {d.sensitivity}")
        if problem.infrastructure_choices:
            lines.append("InfrastructureChoices:")
            for c in problem.infrastructure_choices:
                lines.append(
                    f"  - category={c.category}, technology={c.technology}, "
                    f"version_pin={c.version_pin}"
                )
