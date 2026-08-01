"""Tests for CompletedMetricsReader (resume short-circuit metrics)."""

import json
from pathlib import Path

import pytest

from squeaky_clean.application.evaluation.eval.resume.completed_metrics_reader import (
    CompletedMetricsReader,
)


def test_missing_report_falls_back_to_checkpoint_cost() -> None:
    m = CompletedMetricsReader().read(None, 0.42)
    assert m.estimated_cost_usd == pytest.approx(0.42)
    assert m.tests_pass == 0.0


def test_reads_schema_v2_nested_payload(tmp_path: Path) -> None:
    report = tmp_path / "eval_report.json"
    report.write_text(json.dumps({"metrics": {
        "cost": {"estimated_cost_usd": 0.12},
        "test_outcome": {"tests_pass": 0.75},
    }}))
    m = CompletedMetricsReader().read(report, 9.9)
    assert m.estimated_cost_usd == pytest.approx(0.12)
    assert m.tests_pass == pytest.approx(0.75)


def test_reads_legacy_flat_v1_payload(tmp_path: Path) -> None:
    report = tmp_path / "eval_report.json"
    report.write_text(json.dumps({"metrics": {
        "estimated_cost_usd": 0.3, "tests_pass": 1.0,
    }}))
    m = CompletedMetricsReader().read(report, 9.9)
    assert m.estimated_cost_usd == pytest.approx(0.3)
    assert m.tests_pass == pytest.approx(1.0)


def test_null_values_fall_back(tmp_path: Path) -> None:
    report = tmp_path / "eval_report.json"
    report.write_text(json.dumps({"metrics": {
        "test_outcome": {"tests_pass": None},
    }}))
    m = CompletedMetricsReader().read(report, 0.05)
    assert m.estimated_cost_usd == pytest.approx(0.05)
    assert m.tests_pass == 0.0
