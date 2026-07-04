"""ViolationReport DTO: the categorized Analyze-phase output."""

from dataclasses import dataclass

from squeaky_clean.application.dtos.recovery.architectural_violation import (
    ArchitecturalViolation,
)


@dataclass(frozen=True)
class ViolationReport:
    """All violations found in one recovered artifact, grouped on demand.

    Persisted as ``violations.json`` and fed to the interactive triage step.
    ``by_category`` groups the flat list for review and sharding without
    losing the original order within each category.
    """

    violations: tuple[ArchitecturalViolation, ...]

    def by_category(self) -> dict[str, tuple[ArchitecturalViolation, ...]]:
        """Return violations grouped by category, order preserved."""
        grouped: dict[str, list[ArchitecturalViolation]] = {}
        for violation in self.violations:
            grouped.setdefault(violation.category, []).append(violation)
        return {cat: tuple(items) for cat, items in grouped.items()}
