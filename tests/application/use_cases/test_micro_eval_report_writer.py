"""Tests for MicroEvalReportWriter (R5.4)."""

import json
from pathlib import Path

from squeaky_clean.application.evaluation.microeval.micro_eval_cell import (
    MicroEvalCell,
)
from squeaky_clean.application.evaluation.microeval.micro_eval_report_writer import (
    MicroEvalReportWriter,
)


def _cells() -> tuple[MicroEvalCell, ...]:
    return (
        MicroEvalCell("strategy", "python", True, 0, 2, 0.002),
        MicroEvalCell("strategy", "java", False, 2, 2, 0.004,
                      "interface expected here"),
    )


def test_matrix_md_and_failure_section(tmp_path: Path) -> None:
    md_path = MicroEvalReportWriter().write(tmp_path, _cells())
    md = md_path.read_text()
    assert "| strategy | ❌ (2) | ✅ |" in md  # java sorts before python
    assert "cells: 2  passed: 1  failed: 1" in md
    assert "**strategy/java** (2 errors): interface expected here" in md


def test_json_payload_lists_every_cell(tmp_path: Path) -> None:
    MicroEvalReportWriter().write(tmp_path, _cells())
    payload = json.loads((tmp_path / "micro_eval_report.json").read_text())
    assert len(payload) == 2
    assert payload[0]["pattern"] == "strategy"
    assert payload[1]["compile_errors"] == 2
