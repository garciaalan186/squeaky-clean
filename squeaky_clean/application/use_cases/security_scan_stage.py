"""SecurityScanStage: post-integration secret scan + optional SAST.

Populates EvalMetrics fields ``secret_leaks_detected``, ``sast_high_findings``,
``sast_medium_findings``, ``sast_failed`` and writes ``sast_report.json``.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from squeaky_clean.application.dtos.eval_metrics import EvalMetrics
from squeaky_clean.application.dtos.sast_report import SastReport
from squeaky_clean.application.use_cases.secret_path_scanner import SecretPathScanner
from squeaky_clean.domain.interfaces.sast_runner import SastRunner


class SecurityScanStage:
    """Run secret scan + (optional) SAST against generated code."""

    def __init__(
        self, secret_scanner: SecretPathScanner,
        sast_runner: SastRunner | None,
    ) -> None:
        self._secret: SecretPathScanner = secret_scanner
        self._sast: SastRunner | None = sast_runner

    def apply(
        self, output_dir: Path, metrics: EvalMetrics, enable_sast: bool,
    ) -> None:
        """Mutate ``metrics`` with scan counts; persist sast_report.json."""
        self._apply_secret(output_dir, metrics)
        if enable_sast and self._sast is not None:
            report = self._sast.scan(output_dir / "src")
            self._apply_sast(output_dir, metrics, report)

    def _apply_secret(self, output_dir: Path, metrics: EvalMetrics) -> None:
        total: int = 0
        for sub in ("src", "tests"):
            total += len(self._secret.scan(output_dir / sub))
        metrics.secret_leaks_detected = total

    def _apply_sast(
        self, output_dir: Path, metrics: EvalMetrics, report: SastReport,
    ) -> None:
        metrics.sast_high_findings = report.severity_count("HIGH")
        metrics.sast_medium_findings = report.severity_count("MEDIUM")
        metrics.sast_failed = report.has_high_high()
        try:
            (output_dir / "sast_report.json").write_text(
                json.dumps(
                    {"findings": [asdict(f) for f in report.findings]},
                    indent=2,
                )
            )
        except OSError:
            pass
