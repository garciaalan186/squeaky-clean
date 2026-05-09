"""Tests for EvalResult."""

from pathlib import Path

from squeaky_clean.application.dtos.eval_metrics import EvalMetrics
from squeaky_clean.application.dtos.eval_result_dto import EvalResult


def test_eval_result_bundles_fields() -> None:
    metrics = EvalMetrics.empty()
    result = EvalResult(
        problem_id="P0",
        metrics=metrics,
        report_path=Path("/tmp/report.json"),
    )
    assert result.problem_id == "P0"
    assert result.metrics is metrics
    assert result.report_path == Path("/tmp/report.json")
