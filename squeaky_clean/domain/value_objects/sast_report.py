"""SastReport / SastFinding DTOs: SAST scan results for a generated project."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Severity = Literal["LOW", "MEDIUM", "HIGH"]
Confidence = Literal["LOW", "MEDIUM", "HIGH"]


@dataclass(frozen=True)
class SastFinding:
    """One SAST finding (e.g. one bandit issue) on a generated source file."""

    severity: Severity
    confidence: Confidence
    rule_id: str
    file_path: str
    line: int
    message: str


@dataclass(frozen=True)
class SastReport:
    """Immutable bundle of all SAST findings from one scan."""

    findings: tuple[SastFinding, ...]

    @classmethod
    def empty(cls) -> SastReport:
        """Return a report with no findings (used when SAST tool absent)."""
        return cls(findings=())

    def severity_count(self, severity: Severity) -> int:
        """Number of findings at the given severity (any confidence)."""
        return sum(1 for f in self.findings if f.severity == severity)

    def has_high_high(self) -> bool:
        """True iff any finding is severity=HIGH and confidence=HIGH."""
        return any(
            f.severity == "HIGH" and f.confidence == "HIGH" for f in self.findings
        )
