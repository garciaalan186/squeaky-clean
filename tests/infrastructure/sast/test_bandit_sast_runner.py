"""Unit tests for BanditSastRunner: parsing + bandit-not-installed branch."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from unittest.mock import patch

from squeaky_clean.domain.interfaces.run_logger import RunLogger
from squeaky_clean.domain.value_objects.sast_report import SastReport
from squeaky_clean.infrastructure.sast.bandit_sast_runner import BanditSastRunner


class _RecordingLogger(RunLogger):
    def __init__(self) -> None:
        self.events: list[tuple[str, dict[str, object]]] = []

    def event(self, kind: str, **fields: object) -> None:
        self.events.append((kind, fields))


def test_returns_empty_when_bandit_missing(tmp_path: Path) -> None:
    log = _RecordingLogger()
    with patch.object(shutil, "which", return_value=None):
        report = BanditSastRunner(log).scan(tmp_path)
    assert report == SastReport.empty()
    assert any(kind == "sast_skipped" for kind, _ in log.events)


def test_returns_empty_when_source_dir_missing(tmp_path: Path) -> None:
    with patch.object(shutil, "which", return_value="/usr/bin/bandit"):
        report = BanditSastRunner().scan(tmp_path / "nope")
    assert report == SastReport.empty()


def test_parses_bandit_json_output(tmp_path: Path) -> None:
    raw = json.dumps({"results": [
        {
            "issue_severity": "HIGH",
            "issue_confidence": "HIGH",
            "test_id": "B105",
            "filename": "/x/y.py",
            "line_number": 42,
            "issue_text": "hardcoded password",
        },
        {
            "issue_severity": "MEDIUM",
            "issue_confidence": "MEDIUM",
            "test_id": "B101",
            "filename": "/x/z.py",
            "line_number": 7,
            "issue_text": "use of assert",
        },
    ]})
    runner = BanditSastRunner()
    report = runner._parse(raw)
    assert len(report.findings) == 2
    assert report.severity_count("HIGH") == 1
    assert report.severity_count("MEDIUM") == 1
    assert report.has_high_high() is True


def test_parses_unparseable_json_returns_empty() -> None:
    log = _RecordingLogger()
    runner = BanditSastRunner(log)
    report = runner._parse("not json")
    assert report == SastReport.empty()
    assert any(kind == "sast_output_unparseable" for kind, _ in log.events)


def test_drops_findings_with_invalid_severity() -> None:
    raw = json.dumps({"results": [
        {"issue_severity": "BOGUS", "issue_confidence": "HIGH",
         "test_id": "B0", "filename": "x", "line_number": 1, "issue_text": ""},
    ]})
    report = BanditSastRunner()._parse(raw)
    assert report.findings == ()
