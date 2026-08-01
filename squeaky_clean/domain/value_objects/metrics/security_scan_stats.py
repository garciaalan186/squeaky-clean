"""SecurityScanStats value object: secret-scan + SAST findings (R6.3)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SecurityScanStats:
    """Immutable post-integration security scan results.

    Produced whole by SecurityScanStage (secret scan always; SAST only
    when enabled), so a populated value always reflects one real scan.
    """

    secret_leaks_detected: int = 0
    sast_high_findings: int = 0
    sast_medium_findings: int = 0
    sast_failed: bool = False
