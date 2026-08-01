"""SASTResult: one SAST tool run summary."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SASTResult:
    """One SAST run summary."""

    tool: str
    available: bool
    issues: int
    raw_output: str
