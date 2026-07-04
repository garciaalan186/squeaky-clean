"""ViolationReportSerializer: persist a ViolationReport as violations.json."""

import json

from squeaky_clean.application.dtos.recovery.violation_report import ViolationReport


class ViolationReportSerializer:
    """Serializes a ViolationReport to stable, diff-friendly JSON.

    Each violation is written with its stable ``id`` (so the triage step can
    reference selections across runs), category, target, detail, and
    suggestion. Deterministic key order and indentation keep the artifact
    version-control friendly.
    """

    def serialize(self, report: ViolationReport) -> str:
        """Return the violations.json text for a report."""
        payload = {
            "violations": [
                {
                    "id": v.violation_id, "category": v.category,
                    "target": v.target, "detail": v.detail,
                    "suggestion": v.suggestion,
                }
                for v in report.violations
            ]
        }
        return json.dumps(payload, indent=2, sort_keys=False)
