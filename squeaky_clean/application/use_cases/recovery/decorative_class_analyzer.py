"""DecorativeClassAnalyzer: rule-13 classes with no behavior or invariants."""

from squeaky_clean.application.dtos.recovery.architectural_violation import (
    ArchitecturalViolation,
)
from squeaky_clean.application.dtos.recovery.recovery_artifact import RecoveryArtifact
from squeaky_clean.application.use_cases.recovery.violation_analyzer import (
    ViolationAnalyzer,
)


class DecorativeClassAnalyzer(ViolationAnalyzer):
    """Flags classes with no methods and no invariants (rule 13).

    A class that carries neither behavior nor a construction rule is a
    decorative wrapper the architecture doesn't need; the fix is to fold it
    into the primitive it wraps or give it the behavior it implies.
    """

    def analyze(self, artifact: RecoveryArtifact) -> tuple[ArchitecturalViolation, ...]:
        """Return a violation for each behaviorless, invariant-free class."""
        return tuple(
            ArchitecturalViolation(
                category="decorative-class", target=cls.name,
                detail="no methods and no invariants (rule 13)",
                suggestion="fold into the primitive it wraps, or add behavior",
            )
            for module in artifact.spec.modules
            for cls in module.classes
            if not cls.methods and not cls.invariants
        )
