"""ArchitecturalViolation DTO: one categorized Clean-Architecture finding."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ArchitecturalViolation:
    """A structured, categorized finding against the recovered architecture.

    `category` groups the finding (e.g. ``framework-coupling``,
    ``dependency-rule``). `target` names what it concerns — specific enough
    that ``category:target`` is a stable, unique id for the triage step.
    `detail` states the specifics; `suggestion` names the recommended fix.
    """

    category: str
    target: str
    detail: str
    suggestion: str

    @property
    def violation_id(self) -> str:
        """Stable identifier used by the triage step to select fixes."""
        return f"{self.category}:{self.target}"
