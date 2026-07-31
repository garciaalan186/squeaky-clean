"""Tests for the RegressionAssessment DTO (R5.2)."""

from squeaky_clean.application.evaluation.eval.report.regression_assessment import (
    RegressionAssessment,
)
from squeaky_clean.application.evaluation.eval.report.regression_record import (
    RegressionRecord,
)


def test_defaults_are_empty_and_pass() -> None:
    a = RegressionAssessment()
    assert a.verdicts == () and a.records == ()
    assert not a.has_regressions


def test_has_regressions_when_any_record() -> None:
    record = RegressionRecord(
        metric="tests_pass", problem_id="P2",
        baseline_mean=1.0, baseline_stddev=0.05,
        current_mean=0.1, current_stddev=0.0,
        sigma_drop=18.0, timestamp="2026-07-30T00:00:00+00:00",
    )
    assert RegressionAssessment(records=(record,)).has_regressions
