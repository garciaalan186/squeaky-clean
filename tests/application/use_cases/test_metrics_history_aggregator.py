"""Tests for MetricsHistoryAggregator."""

import json
from pathlib import Path

from squeaky_clean.application.evaluation.eval.metrics.metrics_history_aggregator import (
    MetricsHistoryAggregator,
)


def _make_run(
    root: Path, name: str, metrics: dict[str, object] | None,
    problem_subdir: str | None = "problem-set-0-calculator-code",
) -> None:
    run = root / name
    run.mkdir(parents=True)
    if metrics is not None:
        (run / "metrics.json").write_text(json.dumps(metrics))
    if problem_subdir is not None:
        (run / problem_subdir).mkdir(parents=True)


def test_aggregates_in_run_number_order(tmp_path: Path) -> None:
    _make_run(tmp_path, "meta-evaluation_002_20260411-143828",
              {"tests_pass": 0.5, "estimated_cost_usd": 0.1})
    _make_run(tmp_path, "meta-evaluation_001_20260411-131227",
              {"tests_pass": 1.0, "estimated_cost_usd": 0.2})
    snaps = MetricsHistoryAggregator().aggregate(tmp_path)
    assert len(snaps) == 2
    assert snaps[0].run_number == 1
    assert snaps[1].run_number == 2
    assert snaps[0].timestamp == "20260411-131227"
    assert snaps[0].metrics["tests_pass"] == 1.0
    assert snaps[0].problem_id == "problem-set-0-calculator-code"


def test_skips_dirs_without_metrics_json(tmp_path: Path) -> None:
    _make_run(tmp_path, "meta-evaluation_001_20260411-131227",
              {"tests_pass": 1.0})
    _make_run(tmp_path, "meta-evaluation_002_20260411-143828", None)
    snaps = MetricsHistoryAggregator().aggregate(tmp_path)
    assert len(snaps) == 1
    assert snaps[0].run_number == 1


def test_skips_malformed_json(tmp_path: Path) -> None:
    bad = tmp_path / "meta-evaluation_005_20260411-131227"
    bad.mkdir(parents=True)
    (bad / "metrics.json").write_text("{not json")
    _make_run(tmp_path, "meta-evaluation_001_20260411-131227",
              {"tests_pass": 1.0})
    snaps = MetricsHistoryAggregator().aggregate(tmp_path)
    assert {s.run_number for s in snaps} == {1}


def test_drops_non_numeric_fields(tmp_path: Path) -> None:
    _make_run(tmp_path, "meta-evaluation_001_20260411-131227",
              {"tests_pass": 1.0, "classes_per_module": [1, 2, 3],
               "budget_exceeded": True, "label": "ok"})
    snaps = MetricsHistoryAggregator().aggregate(tmp_path)
    assert "tests_pass" in snaps[0].metrics
    assert "classes_per_module" not in snaps[0].metrics
    assert "budget_exceeded" not in snaps[0].metrics
    assert "label" not in snaps[0].metrics


def test_flattens_schema_v2_nested_payloads_to_v1_keys(tmp_path: Path) -> None:
    """Schema v2 VO nesting must yield the same snapshot keys as v1 files."""
    _make_run(tmp_path, "meta-evaluation_001_20260411-131227", {
        "schema_version": 2,
        "test_outcome": {"tests_pass": 0.9, "test_status": "ok"},
        "cost": {"estimated_cost_usd": 0.3},
        "security_scan": {"secret_leaks_detected": 1},
        "cache_by_tier": {"icp": {"create_tokens": 5}},
        "total_wall_clock_ms": 1200,
    })
    snaps = MetricsHistoryAggregator().aggregate(tmp_path)
    m = snaps[0].metrics
    assert m["tests_pass"] == 0.9
    assert m["estimated_cost_usd"] == 0.3
    assert m["secret_leaks_detected"] == 1
    assert m["total_wall_clock_ms"] == 1200
    # Per-tier cache leaves must NOT be promoted (they would collide).
    assert "create_tokens" not in m


def test_top_level_scalars_win_over_nested_leaves(tmp_path: Path) -> None:
    _make_run(tmp_path, "meta-evaluation_001_20260411-131227", {
        "total_wall_clock_ms": 7,
        "cost": {"total_wall_clock_ms": 99},
    })
    snaps = MetricsHistoryAggregator().aggregate(tmp_path)
    assert snaps[0].metrics["total_wall_clock_ms"] == 7


def test_missing_root_returns_empty(tmp_path: Path) -> None:
    snaps = MetricsHistoryAggregator().aggregate(tmp_path / "nope")
    assert snaps == ()


def test_problem_id_empty_when_no_subdir(tmp_path: Path) -> None:
    _make_run(tmp_path, "meta-evaluation_001_2026", {"tests_pass": 1.0},
              problem_subdir=None)
    snaps = MetricsHistoryAggregator().aggregate(tmp_path)
    assert snaps[0].problem_id == ""
