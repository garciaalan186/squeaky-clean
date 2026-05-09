"""Tests for the RunMetricsSnapshot DTO."""

from squeaky_clean.application.dtos.run_metrics_snapshot import RunMetricsSnapshot


def test_snapshot_is_frozen() -> None:
    snap = RunMetricsSnapshot(
        run_number=1, timestamp="20260411-131227",
        metrics={"tests_pass": 1.0}, problem_id="problem-set-0-calculator-code",
    )
    try:
        snap.run_number = 2  # type: ignore[misc]
    except Exception:
        return
    raise AssertionError("RunMetricsSnapshot should be frozen")


def test_snapshot_carries_all_fields() -> None:
    snap = RunMetricsSnapshot(
        run_number=42, timestamp="20260101-000000",
        metrics={"a": 1, "b": 2.5}, problem_id="problem-set-1-todo-api-code",
    )
    assert snap.run_number == 42
    assert snap.timestamp == "20260101-000000"
    assert snap.metrics == {"a": 1, "b": 2.5}
    assert snap.problem_id == "problem-set-1-todo-api-code"
