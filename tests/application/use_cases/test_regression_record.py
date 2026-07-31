"""Tests for the RegressionRecord DTO."""

import dataclasses

import pytest

from squeaky_clean.application.evaluation.eval.report.regression_record import RegressionRecord


def _record() -> RegressionRecord:
    return RegressionRecord(
        metric="tests_pass", problem_id="P0",
        baseline_mean=0.9, baseline_stddev=0.05,
        current_mean=0.6, current_stddev=0.1,
        sigma_drop=6.0, timestamp="20260730-120000",
    )


def test_stores_all_fields() -> None:
    record = _record()
    assert record.metric == "tests_pass"
    assert record.problem_id == "P0"
    assert record.baseline_mean == 0.9
    assert record.current_mean == 0.6
    assert record.sigma_drop == 6.0
    assert record.timestamp == "20260730-120000"


def test_is_frozen() -> None:
    record = _record()
    with pytest.raises(dataclasses.FrozenInstanceError):
        record.sigma_drop = 0.0  # type: ignore[misc]


def test_equality_is_by_value() -> None:
    assert _record() == _record()
