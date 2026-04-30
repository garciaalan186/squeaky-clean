"""Unit tests for BanditSastRunner: parsing + bandit-not-installed branch."""

from __future__ import annotations

import json
import logging
import shutil
from pathlib import Path
from unittest.mock import patch

import pytest

from squeaky_clean.application.dtos.sast_report import SastReport
from squeaky_clean.infrastructure.sast.bandit_sast_runner import BanditSastRunner


def test_returns_empty_when_bandit_missing(
    tmp_path: Path, caplog: pytest.LogCaptureFixture,
) -> None:
    caplog.set_level(logging.WARNING)
    with patch.object(shutil, "which", return_value=None):
        report = BanditSastRunner().scan(tmp_path)
    assert report == SastReport.empty()
    assert any("bandit not installed" in r.message for r in caplog.records)


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
    runner = BanditSastRunner()
    report = runner._parse("not json")
    assert report == SastReport.empty()


def test_drops_findings_with_invalid_severity() -> None:
    raw = json.dumps({"results": [
        {"issue_severity": "BOGUS", "issue_confidence": "HIGH",
         "test_id": "B0", "filename": "x", "line_number": 1, "issue_text": ""},
    ]})
    report = BanditSastRunner()._parse(raw)
    assert report.findings == ()
