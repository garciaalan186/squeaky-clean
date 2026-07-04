"""FrameworkCouplingAnalyzer: framework-coupling category (wraps Milestone L)."""

from squeaky_clean.application.dtos.recovery.architectural_violation import (
    ArchitecturalViolation,
)
from squeaky_clean.application.dtos.recovery.recovery_artifact import RecoveryArtifact
from squeaky_clean.application.use_cases.recovery.framework_coupling_detector import (
    FrameworkCouplingDetector,
)
from squeaky_clean.application.use_cases.recovery.violation_analyzer import (
    ViolationAnalyzer,
)


class FrameworkCouplingAnalyzer(ViolationAnalyzer):
    """Reports domain classes coupled to a framework base as violations.

    Adapts the Milestone-L detector into the violation model: each
    RefactorProposal becomes a ``framework-coupling`` violation whose
    suggestion names the Entity + Repository + Adapter split.
    """

    def __init__(self) -> None:
        self._detector: FrameworkCouplingDetector = FrameworkCouplingDetector()

    def analyze(self, artifact: RecoveryArtifact) -> tuple[ArchitecturalViolation, ...]:
        """Return a violation for each framework-coupled domain class."""
        return tuple(
            ArchitecturalViolation(
                category="framework-coupling", target=proposal.fqn,
                detail=f"inherits framework base {proposal.foreign_base!r}",
                suggestion=f"split into {proposal.entity} + "
                           f"{proposal.repository} + {proposal.adapter}",
            )
            for proposal in self._detector.detect_all(
                artifact.catalog, artifact.layers,
            )
        )
