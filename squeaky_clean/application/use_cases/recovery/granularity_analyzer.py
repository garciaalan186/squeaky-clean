"""GranularityAnalyzer: classes exceeding the public-method bound."""

from squeaky_clean.application.dtos.recovery.architectural_violation import (
    ArchitecturalViolation,
)
from squeaky_clean.application.dtos.recovery.recovery_artifact import RecoveryArtifact
from squeaky_clean.application.use_cases.recovery.violation_analyzer import (
    ViolationAnalyzer,
)

_MAX_METHODS: int = 5


class GranularityAnalyzer(ViolationAnalyzer):
    """Flags classes with more than five public methods (SRP smell).

    A god-class carried over from the original violates the same ≤5-method
    bound the framework enforces on generated code; the fix is to decompose
    it (Strategy/Facade or extract a collaborator).
    """

    def analyze(self, artifact: RecoveryArtifact) -> tuple[ArchitecturalViolation, ...]:
        """Return a violation for each class exceeding the method bound."""
        return tuple(
            ArchitecturalViolation(
                category="granularity", target=cls.name,
                detail=f"{len(cls.methods)} public methods (>{_MAX_METHODS})",
                suggestion="decompose via Strategy/Facade or extract a collaborator",
            )
            for module in artifact.spec.modules
            for cls in module.classes
            if len(cls.methods) > _MAX_METHODS
        )
