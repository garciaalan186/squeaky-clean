"""Tests for the ReplicateReport DTO (R5.1)."""

from squeaky_clean.application.evaluation.eval.sweep.replicate_aggregator import (
    ReplicateAggregator,
)
from squeaky_clean.application.evaluation.eval.sweep.replicate_report import (
    ReplicateReport,
)


def test_defaults_to_no_reports() -> None:
    summary = ReplicateAggregator().aggregate("P0", [])
    report = ReplicateReport(summary=summary)
    assert report.report_paths == ()
    assert report.summary.problem_id == "P0"


def test_is_frozen() -> None:
    summary = ReplicateAggregator().aggregate("P0", [])
    report = ReplicateReport(summary=summary, report_paths=("a",))
    try:
        report.report_paths = ("b",)  # type: ignore[misc]
        raise AssertionError("expected FrozenInstanceError")
    except Exception as exc:  # noqa: BLE001
        assert type(exc).__name__ == "FrozenInstanceError"
