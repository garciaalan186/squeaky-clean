"""ViolationAnalysis: run every analyzer over a recovered artifact."""

from squeaky_clean.application.dtos.recovery.recovery_artifact import RecoveryArtifact
from squeaky_clean.application.dtos.recovery.violation_report import ViolationReport
from squeaky_clean.application.use_cases.recovery.cyclic_dependency_analyzer import (
    CyclicDependencyAnalyzer,
)
from squeaky_clean.application.use_cases.recovery.decorative_class_analyzer import (
    DecorativeClassAnalyzer,
)
from squeaky_clean.application.use_cases.recovery.dependency_rule_analyzer import (
    DependencyRuleAnalyzer,
)
from squeaky_clean.application.use_cases.recovery.framework_coupling_analyzer import (
    FrameworkCouplingAnalyzer,
)
from squeaky_clean.application.use_cases.recovery.granularity_analyzer import (
    GranularityAnalyzer,
)
from squeaky_clean.application.use_cases.recovery.violation_analyzer import (
    ViolationAnalyzer,
)


class ViolationAnalysis:
    """Analyze phase: run the analyzer suite and return a ViolationReport.

    Deterministic — no LLM. Points the framework's own generated-code rules
    inward at the faithful recovered artifact, aggregating every analyzer's
    findings into one categorized report for triage.
    """

    def __init__(self) -> None:
        self._analyzers: tuple[ViolationAnalyzer, ...] = (
            FrameworkCouplingAnalyzer(), DependencyRuleAnalyzer(),
            CyclicDependencyAnalyzer(), GranularityAnalyzer(),
            DecorativeClassAnalyzer(),
        )

    def analyze(self, artifact: RecoveryArtifact) -> ViolationReport:
        """Return the aggregated ViolationReport for the artifact."""
        return ViolationReport(violations=tuple(
            v for analyzer in self._analyzers for v in analyzer.analyze(artifact)
        ))
