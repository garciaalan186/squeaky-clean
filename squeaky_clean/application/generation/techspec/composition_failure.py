"""CompositionFailure: a TechSpec composition rejected by validation (H2)."""

from dataclasses import dataclass

from squeaky_clean.application.generation.emission.class_assignment import ClassAssignment
from squeaky_clean.domain.value_objects.tech_spec import TechSpec


@dataclass(frozen=True)
class CompositionFailure:
    """One failed (assignment, tech_spec) composition and its errors.

    Produced by TechSpecComposer when validation rejects a composition;
    carried into the Manager-tier correction call and its prompt assembly.
    """

    assignment: ClassAssignment
    tech_spec: TechSpec
    errors: tuple[str, ...]
