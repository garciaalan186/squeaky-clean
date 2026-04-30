"""ValidateArchitectureAgainstSpec: enforce ProblemSpec semantics on architecture."""

from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.application.use_cases.convention_to_invariant import (
    ConventionToInvariant,
)
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec


class SpecConformanceError(ValueError):
    """Raised when an architecture violates the ProblemSpec semantic contract."""


class ValidateArchitectureAgainstSpec:
    """Cross-checks an ArchitectureSpec against ProblemSpec semantic fields."""

    def __init__(self) -> None:
        self._conv: ConventionToInvariant = ConventionToInvariant()

    def execute(
        self, arch: ArchitectureSpec, problem: ProblemSpec,
    ) -> tuple[str, ...]:
        """Return tuple of violation strings; empty when fully conformant."""
        invariants = self._all_invariants(arch)
        class_names = {c.name for m in arch.modules for c in m.classes}
        entity_names = {c.name for m in arch.modules for c in m.classes
                        if c.pattern == "Entity"}
        fields = self._fields_by_class(arch)
        violations: list[str] = []
        for tag in problem.domain_conventions:
            text = self._conv.lookup(tag)
            if not any(text in inv for inv in invariants):
                violations.append(
                    f"convention {tag!r} expected as INVARIANT but not found")
        for q in problem.query_semantics:
            if q.use_case not in class_names:
                violations.append(
                    f"QuerySemantics use_case {q.use_case!r} matches no class")
        for el in problem.entity_lifecycle:
            if el.entity not in entity_names:
                violations.append(
                    f"EntityLifecycle entity {el.entity!r} matches no Entity class")
        for d in problem.data_classification:
            cls, _, fld = d.field_ref.partition(".")
            normalized = self._normalize(fld)
            class_fields = {self._normalize(f) for f in fields.get(cls, set())}
            if cls not in fields or normalized not in class_fields:
                violations.append(
                    f"DataClassification field_ref {d.field_ref!r} not found")
        return tuple(violations)

    @staticmethod
    def _normalize(name: str) -> str:
        """Lowercase + strip underscores so snake_case ↔ camelCase matches."""
        return name.lower().replace("_", "")

    def _all_invariants(self, arch: ArchitectureSpec) -> list[str]:
        return [inv for m in arch.modules for inv in m.invariants] + [
            inv for m in arch.modules for c in m.classes for inv in c.invariants]

    def _fields_by_class(
        self, arch: ArchitectureSpec,
    ) -> dict[str, set[str]]:
        out: dict[str, set[str]] = {}
        for m in arch.modules:
            for c in m.classes:
                out[c.name] = {
                    f.split(":", 1)[0].strip() for f in c.fields if ":" in f
                }
        return out
