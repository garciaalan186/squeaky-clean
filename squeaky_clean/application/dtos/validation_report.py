"""ValidationReport DTO: result of running architecture rules over a project."""

from dataclasses import dataclass

from squeaky_clean.application.dtos.violation import Violation


@dataclass(frozen=True)
class ValidationReport:
    """Immutable bundle of rule violations plus files-scanned count.

    `violations` is the full list of violations detected across all
    rules (empty if clean). `files_scanned` is how many Python files
    were inspected. `is_valid` is a convenience property that mirrors
    ``len(violations) == 0``.
    """

    violations: tuple[Violation, ...]
    files_scanned: int

    @property
    def is_valid(self) -> bool:
        """Return True iff no violations were recorded."""
        return len(self.violations) == 0
