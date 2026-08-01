"""Unit tests for SecurityScanStage (pipeline secret + SAST integration)."""

from __future__ import annotations

import json
from pathlib import Path

from squeaky_clean.application.generation.security.secret_path_scanner import SecretPathScanner
from squeaky_clean.application.generation.security.security_scan_stage import SecurityScanStage
from squeaky_clean.domain.interfaces.sast_runner import SastRunner
from squeaky_clean.domain.value_objects.sast_report import SastFinding, SastReport


class _StubRunner(SastRunner):
    def __init__(self, report: SastReport) -> None:
        self._report = report
        self.calls: list[Path] = []

    def scan(self, source_dir: Path) -> SastReport:
        self.calls.append(source_dir)
        return self._report


def _hh() -> SastFinding:
    return SastFinding(
        severity="HIGH", confidence="HIGH", rule_id="B105",
        file_path="x.py", line=1, message="hardcoded pw",
    )


def _med() -> SastFinding:
    return SastFinding(
        severity="MEDIUM", confidence="LOW", rule_id="B101",
        file_path="y.py", line=1, message="assert",
    )


_FAKE_KEY = "sk-ant" + "-abcdefghij0123456789ABC"


def test_secret_leak_in_generated_src_populates_metric(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "leak.py").write_text(f"k = '{_FAKE_KEY}'\n")
    stats = SecurityScanStage(SecretPathScanner(), None).apply(tmp_path, False)
    assert stats.secret_leaks_detected == 1


def test_no_leak_when_clean(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "ok.py").write_text("print('hi')\n")
    stats = SecurityScanStage(SecretPathScanner(), None).apply(tmp_path, False)
    assert stats.secret_leaks_detected == 0


def test_sast_skipped_when_disabled(tmp_path: Path) -> None:
    runner = _StubRunner(SastReport(findings=(_hh(),)))
    stats = SecurityScanStage(SecretPathScanner(), runner).apply(tmp_path, False)
    assert runner.calls == []
    assert stats.sast_failed is False


def test_sast_high_high_flips_failed_flag(tmp_path: Path) -> None:
    runner = _StubRunner(SastReport(findings=(_hh(), _med())))
    stats = SecurityScanStage(SecretPathScanner(), runner).apply(tmp_path, True)
    assert stats.sast_high_findings == 1
    assert stats.sast_medium_findings == 1
    assert stats.sast_failed is True
    payload = json.loads((tmp_path / "sast_report.json").read_text())
    assert len(payload["findings"]) == 2


def test_sast_medium_only_does_not_fail(tmp_path: Path) -> None:
    runner = _StubRunner(SastReport(findings=(_med(),)))
    stats = SecurityScanStage(SecretPathScanner(), runner).apply(tmp_path, True)
    assert stats.sast_failed is False
    assert stats.sast_medium_findings == 1
