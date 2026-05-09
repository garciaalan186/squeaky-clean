"""Unit tests for RegressionWriter."""

import json
from pathlib import Path

from squeaky_clean.application.dtos.regression_record import RegressionRecord
from squeaky_clean.application.use_cases.regression_writer import RegressionWriter


def _record(metric: str = "tests_pass") -> RegressionRecord:
    return RegressionRecord(
        metric=metric, problem_id="P0",
        baseline_mean=1.0, baseline_stddev=0.05,
        current_mean=0.5, current_stddev=0.1,
        sigma_drop=10.0, timestamp="2026-04-25T00:00:00Z",
    )


def test_writes_new_file(tmp_path: Path) -> None:
    target = tmp_path / "reports" / "regressions.json"
    RegressionWriter().write([_record()], target)
    data = json.loads(target.read_text())
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["metric"] == "tests_pass"


def test_appends_to_existing_file(tmp_path: Path) -> None:
    target = tmp_path / "regressions.json"
    RegressionWriter().write([_record("a")], target)
    RegressionWriter().write([_record("b")], target)
    data = json.loads(target.read_text())
    assert len(data) == 2
    assert {row["metric"] for row in data} == {"a", "b"}


def test_corrupt_file_is_replaced(tmp_path: Path) -> None:
    target = tmp_path / "regressions.json"
    target.write_text("not valid json {")
    RegressionWriter().write([_record()], target)
    data = json.loads(target.read_text())
    assert len(data) == 1
