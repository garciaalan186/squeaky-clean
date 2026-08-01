"""SastFinding: one SAST finding on a generated source file."""

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
