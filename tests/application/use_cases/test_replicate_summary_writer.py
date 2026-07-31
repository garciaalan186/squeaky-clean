"""Tests for ReplicateSummaryWriter (R5.1)."""

import json
from pathlib import Path

from squeaky_clean.application.evaluation.eval.sweep.replicate_report import (
    ReplicateReport,
)
from squeaky_clean.application.evaluation.eval.sweep.replicate_summary import (
    ReplicateSummary,
)
from squeaky_clean.application.evaluation.eval.sweep.replicate_summary_writer import (
    ReplicateSummaryWriter,
)


def _summary(n: int) -> ReplicateSummary:
    return ReplicateSummary(
        problem_id="P2", replicates=n,
        tests_pass_mean=0.83, tests_pass_stddev=0.29,
        functional_pass_mean=0.83, functional_pass_stddev=0.29,
        security_pass_mean=0.0, security_pass_stddev=0.0,
        cost_usd_mean=0.06, cost_usd_stddev=0.01,
        wall_clock_ms_mean=1000.0, wall_clock_ms_stddev=100.0,
        cache_hit_ratio=0.5,
    )


def test_writes_json_with_all_stats_and_reports(tmp_path: Path) -> None:
    path = ReplicateSummaryWriter().write(tmp_path, ReplicateReport(
        summary=_summary(3),
        report_paths=("a/eval_report.json", "b/eval_report.json"),
    ))
    payload = json.loads(path.read_text())
    assert payload["replicates"] == 3
    assert payload["tests_pass_mean"] == 0.83
    assert payload["wall_clock_ms_stddev"] == 100.0
    assert payload["reports"] == ["a/eval_report.json", "b/eval_report.json"]


def test_markdown_has_sigma_table_and_no_label_at_threshold(
    tmp_path: Path,
) -> None:
    ReplicateSummaryWriter().write(tmp_path, ReplicateReport(_summary(3)))
    md = (tmp_path / "replicate_summary.md").read_text()
    assert "N=3" in md and "| tests_pass | 0.83 | 0.29 |" in md
    assert "exploratory" not in md


def test_markdown_labels_below_threshold_exploratory(tmp_path: Path) -> None:
    ReplicateSummaryWriter().write(tmp_path, ReplicateReport(_summary(1)))
    md = (tmp_path / "replicate_summary.md").read_text()
    assert "below the claims threshold" in md and "exploratory" in md


def test_failures_rendered_in_md_and_json(tmp_path: Path) -> None:
    path = ReplicateSummaryWriter().write(tmp_path, ReplicateReport(
        summary=_summary(2),
        failures=("replicate 1: DesignArchitectureError: unbalanced {}",),
    ))
    payload = json.loads(path.read_text())
    assert payload["failures"] == [
        "replicate 1: DesignArchitectureError: unbalanced {}",
    ]
    md = (tmp_path / "replicate_summary.md").read_text()
    assert "1 replicate(s) FAILED" in md
