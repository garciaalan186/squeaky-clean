"""ViolationReportDeserializer: load a persisted violations.json report."""

import json

from squeaky_clean.application.dtos.recovery.architectural_violation import (
    ArchitecturalViolation,
)
from squeaky_clean.application.dtos.recovery.violation_report import ViolationReport


class ViolationReportDeserializer:
    """Rebuilds a ViolationReport from its persisted JSON.

    The inverse of ViolationReportSerializer, so the triage step can run
    against a previously-analyzed artifact without re-running analysis —
    each phase is independently re-runnable from its persisted output.
    """

    def deserialize(self, text: str) -> ViolationReport:
        """Return the ViolationReport encoded in ``text``."""
        data = json.loads(text)
        return ViolationReport(tuple(
            ArchitecturalViolation(
                category=entry["category"], target=entry["target"],
                detail=entry["detail"], suggestion=entry["suggestion"],
            )
            for entry in data["violations"]
        ))
