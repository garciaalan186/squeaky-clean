"""CyclicDependencyAnalyzer: module-level dependency cycle violations."""

from squeaky_clean.application.dtos.recovery.architectural_violation import (
    ArchitecturalViolation,
)
from squeaky_clean.application.dtos.recovery.recovery_artifact import RecoveryArtifact
from squeaky_clean.application.use_cases.recovery.violation_analyzer import (
    ViolationAnalyzer,
)


class CyclicDependencyAnalyzer(ViolationAnalyzer):
    """Reports module dependency cycles as violations.

    The ArchitectureGraph must be a DAG; each cycle it reports becomes a
    ``cyclic-dependency`` violation whose fix is to invert one edge behind
    a port so the graph acyclifies.
    """

    def analyze(self, artifact: RecoveryArtifact) -> tuple[ArchitecturalViolation, ...]:
        """Return a violation for each module cycle in the artifact."""
        return tuple(
            ArchitecturalViolation(
                category="cyclic-dependency", target=cycle,
                detail=f"module dependency cycle: {cycle}",
                suggestion="break the cycle by inverting one dependency behind a port",
            )
            for cycle in artifact.spec.graph.cycle_violations()
        )
