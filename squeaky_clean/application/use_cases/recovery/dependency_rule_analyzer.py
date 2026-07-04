"""DependencyRuleAnalyzer: inner-layer-imports-outer-layer violations."""

from squeaky_clean.application.dtos.recovery.architectural_violation import (
    ArchitecturalViolation,
)
from squeaky_clean.application.dtos.recovery.recovery_artifact import RecoveryArtifact
from squeaky_clean.application.use_cases.recovery.violation_analyzer import (
    ViolationAnalyzer,
)
from squeaky_clean.domain.value_objects.layer_type import LayerType

_RANK: dict[LayerType, int] = {
    LayerType.DOMAIN: 0, LayerType.APPLICATION: 1,
    LayerType.INFRASTRUCTURE: 2, LayerType.INTERFACE: 3,
}


class DependencyRuleAnalyzer(ViolationAnalyzer):
    """Flags any class importing a sibling in a strictly outer layer.

    The Dependency Rule: source dependencies point only inward. Ranking
    Domain<Application<Infrastructure<Interface, an import from a lower rank
    to a higher rank (inner depending on outer) is a violation. Reported
    per offending edge so ``category:target`` stays unique.
    """

    def analyze(self, artifact: RecoveryArtifact) -> tuple[ArchitecturalViolation, ...]:
        """Return a violation for each inner->outer import edge."""
        layers = artifact.layers
        out: list[ArchitecturalViolation] = []
        for fqn, deps in artifact.catalog.import_graph.items():
            src = layers.get(fqn)
            if src is None:
                continue
            for dep in deps:
                dst = layers.get(dep)
                if dst is not None and _RANK[dst] > _RANK[src]:
                    out.append(self._violation(fqn, dep, src, dst))
        return tuple(out)

    def _violation(
        self, fqn: str, dep: str, src: LayerType, dst: LayerType,
    ) -> ArchitecturalViolation:
        return ArchitecturalViolation(
            category="dependency-rule",
            target=f"{fqn.rsplit('.', 1)[-1]}->{dep.rsplit('.', 1)[-1]}",
            detail=f"{src.value} class imports {dst.value} class",
            suggestion="invert the dependency behind a port in the inner layer",
        )
