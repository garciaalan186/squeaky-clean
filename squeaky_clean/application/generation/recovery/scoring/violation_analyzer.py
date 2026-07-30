"""ViolationAnalyzer port: one category of architectural violation check."""

from abc import ABC, abstractmethod

from squeaky_clean.application.generation.recovery.refactor.recovery_artifact import (
    RecoveryArtifact,
)
from squeaky_clean.application.generation.recovery.scoring.architectural_violation import (
    ArchitecturalViolation,
)


class ViolationAnalyzer(ABC):
    """Port for a single deterministic violation check over the artifact.

    Each concrete analyzer inspects the faithful RecoveryArtifact and
    returns the violations in its category. Keeping them behind one port
    lets ViolationAnalysis run an extensible set and lets new categories be
    added without touching the orchestrator. No analyzer calls an LLM.
    """

    @abstractmethod
    def analyze(self, artifact: RecoveryArtifact) -> tuple[ArchitecturalViolation, ...]:
        """Return this analyzer's violations for the recovered artifact."""
