"""RunEvalReportWriter: writes per-problem eval_report.json to disk."""

import json
from dataclasses import asdict
from pathlib import Path

from squeaky_clean.application.dtos.eval_report_bundle import EvalReportBundle


class RunEvalReportWriter:
    """Writes the per-problem ``eval_report.json`` artifact as JSON."""

    def write(self, path: Path, bundle: EvalReportBundle) -> None:
        """Serialise ``bundle`` as JSON into ``path``, creating parent dirs."""
        path.parent.mkdir(parents=True, exist_ok=True)
        payload: dict[str, object] = {
            "problem_id": bundle.problem.id,
            "description": bundle.problem.description,
            "metrics": asdict(bundle.metrics),
            "tests": {
                "passed": bundle.test_run_result.passed,
                "failed": bundle.test_run_result.failed,
                "errors": bundle.test_run_result.errors,
                "duration_ms": bundle.test_run_result.duration_ms,
            },
            "violations": [
                {
                    "rule_name": v.rule_name,
                    "file_path": v.file_path,
                    "message": v.message,
                }
                for v in bundle.validation.violations
            ],
            "files_scanned": bundle.validation.files_scanned,
            "acceptance_criteria": bundle.problem.acceptance_criteria,
        }
        path.write_text(json.dumps(payload, indent=2, default=str))
