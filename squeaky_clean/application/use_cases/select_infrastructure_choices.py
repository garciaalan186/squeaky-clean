"""select_infrastructure_choices: explicit + (optional) MCDA-derived picks."""

from __future__ import annotations

from typing import TYPE_CHECKING

from squeaky_clean.application.dtos.infrastructure_choice import InfrastructureChoice
from squeaky_clean.application.dtos.problem_spec import ProblemSpec

if TYPE_CHECKING:
    from squeaky_clean.application.use_cases.infrastructure_choice_architect import (
        InfrastructureChoiceArchitect,
    )


class MissingInfrastructureChoiceError(KeyError):
    """Raised when a category is required but not declared and inference is off."""


def select_infrastructure_choices(
    problem: ProblemSpec,
    required_categories: frozenset[str],
    infer_enabled: bool,
    choice_architect: InfrastructureChoiceArchitect | None = None,
) -> tuple[InfrastructureChoice, ...]:
    """Return the union of explicit and (if enabled) derived choices."""
    explicit: dict[str, InfrastructureChoice] = {
        c.category: c for c in problem.infrastructure_choices
    }
    chosen: list[InfrastructureChoice] = list(explicit.values())
    for cat in sorted(required_categories):
        if cat in explicit:
            continue
        if not infer_enabled or choice_architect is None:
            raise MissingInfrastructureChoiceError(
                f"category={cat!r} not declared in ProblemSpec.infrastructure_choices "
                f"and --infer-infrastructure is OFF; declare or enable inference"
            )
        derived = choice_architect.decide(problem, cat)
        chosen.append(derived.to_choice())
    return tuple(chosen)
