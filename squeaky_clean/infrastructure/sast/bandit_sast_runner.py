"""BanditSastRunner: shell out to ``bandit -r -f json`` and parse findings."""

from __future__ import annotations

import json
import logging
import shutil
import subprocess
from pathlib import Path
from typing import cast

from squeaky_clean.application.dtos.sast_report import (
    Confidence,
    SastFinding,
    SastReport,
    Severity,
)
from squeaky_clean.domain.interfaces.sast_runner import SastRunner

_log = logging.getLogger(__name__)
_TIMEOUT_S: int = 120
_VALID_SEVERITY: frozenset[str] = frozenset({"LOW", "MEDIUM", "HIGH"})


class BanditSastRunner(SastRunner):
    """SastRunner adapter that invokes the ``bandit`` CLI as a subprocess."""

    def scan(self, source_dir: Path) -> SastReport:
        """Run bandit on ``source_dir``; return empty report if absent/missing."""
        if shutil.which("bandit") is None:
            _log.warning("bandit not installed; SAST scan skipped (opt-in dep)")
            return SastReport.empty()
        if not source_dir.exists():
            return SastReport.empty()
        proc = subprocess.run(
            ["bandit", "-r", str(source_dir), "-f", "json", "-q"],
            capture_output=True, text=True, timeout=_TIMEOUT_S, check=False,
        )
        return self._parse(proc.stdout)

    def _parse(self, raw: str) -> SastReport:
        try:
            payload = cast(dict[str, object], json.loads(raw))
        except json.JSONDecodeError:
            _log.warning("bandit produced unparseable JSON; treating as empty")
            return SastReport.empty()
        results_raw = payload.get("results", ())
        if not isinstance(results_raw, list):
            return SastReport.empty()
        findings = tuple(
            f for f in (self._finding(cast(dict[str, object], r))
                        for r in results_raw if isinstance(r, dict))
            if f is not None
        )
        return SastReport(findings=findings)

    def _finding(self, r: dict[str, object]) -> SastFinding | None:
        sev = str(r.get("issue_severity", "")).upper()
        conf = str(r.get("issue_confidence", "")).upper()
        if sev not in _VALID_SEVERITY or conf not in _VALID_SEVERITY:
            return None
        return SastFinding(
            severity=cast(Severity, sev),
            confidence=cast(Confidence, conf),
            rule_id=str(r.get("test_id", "")),
            file_path=str(r.get("filename", "")),
            line=int(cast(int, r.get("line_number", 0)) or 0),
            message=str(r.get("issue_text", "")),
        )
