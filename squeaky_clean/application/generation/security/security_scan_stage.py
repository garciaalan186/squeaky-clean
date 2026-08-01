"""SecurityScanStage: post-integration secret scan + optional SAST.

Builds the frozen SecurityScanStats VO (``secret_leaks_detected``,
``sast_high_findings``, ``sast_medium_findings``, ``sast_failed``),
returns a new EvalMetrics carrying it, and writes ``sast_report.json``.
"""

from __future__ import annotations

import json
from dataclasses import asdict, replace
from pathlib import Path

from squeaky_clean.application.generation.security.secret_path_scanner import SecretPathScanner
from squeaky_clean.application.shared.io.atomic_write import atomic_write_text
from squeaky_clean.domain.interfaces.run_logger import NullRunLogger, RunLogger
from squeaky_clean.domain.interfaces.sast_runner import SastRunner
from squeaky_clean.domain.value_objects.metrics.security_scan_stats import SecurityScanStats
from squeaky_clean.domain.value_objects.sast_report import SastReport


class SecurityScanStage:
    """Run secret scan + (optional) SAST against generated code."""

    def __init__(
        self, secret_scanner: SecretPathScanner,
        sast_runner: SastRunner | None,
        *, logger: RunLogger | None = None,
    ) -> None:
        self._secret: SecretPathScanner = secret_scanner
        self._sast: SastRunner | None = sast_runner
        self._log: RunLogger = logger or NullRunLogger()

    def apply(
        self, output_dir: Path, enable_sast: bool,
    ) -> SecurityScanStats:
        """Return the scan stats VO; persist sast_report.json."""
        scan = SecurityScanStats(
            secret_leaks_detected=self._count_secrets(output_dir),
        )
        if enable_sast and self._sast is not None:
            report = self._sast.scan(output_dir / "src")
            scan = replace(
                scan,
                sast_high_findings=report.severity_count("HIGH"),
                sast_medium_findings=report.severity_count("MEDIUM"),
                sast_failed=report.has_high_high(),
            )
            self._write_report(output_dir, report)
        return scan

    def _count_secrets(self, output_dir: Path) -> int:
        total: int = 0
        for sub in ("src", "tests"):
            total += len(self._secret.scan(output_dir / sub))
        return total

    def _write_report(self, output_dir: Path, report: SastReport) -> None:
        """Persist sast_report.json; a failed write is logged, never silent."""
        path = output_dir / "sast_report.json"
        try:
            atomic_write_text(path, json.dumps(
                {"findings": [asdict(f) for f in report.findings]}, indent=2,
            ))
        except OSError as exc:
            self._log.event("sast_report_write_failed",
                            path=str(path), error=str(exc))
