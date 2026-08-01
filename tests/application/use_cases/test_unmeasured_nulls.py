"""Tests for unmeasured_nulls (R5.3: unmeasured != 0.0; schema v2 nesting)."""

from dataclasses import asdict
from typing import cast

from squeaky_clean.application.evaluation.eval.metrics.unmeasured_nulls import (
    null_unmeasured,
)
from squeaky_clean.domain.entities.eval_metrics import EvalMetrics
from squeaky_clean.domain.value_objects.metrics.test_outcome import TestOutcome


def _outcome(payload: dict[str, object]) -> dict[str, object]:
    return cast("dict[str, object]", payload["test_outcome"])


def test_stamps_schema_version_2() -> None:
    payload = null_unmeasured(asdict(EvalMetrics()))
    assert payload["schema_version"] == 2


def test_security_score_nulled_when_no_security_tests() -> None:
    payload = null_unmeasured(asdict(EvalMetrics(test_outcome=TestOutcome(
        security_tests_pass=0.0, security_test_count=0,
    ))))
    assert _outcome(payload)["security_tests_pass"] is None


def test_measured_security_score_kept() -> None:
    payload = null_unmeasured(asdict(EvalMetrics(test_outcome=TestOutcome(
        security_tests_pass=0.75, security_test_count=4,
    ))))
    assert _outcome(payload)["security_tests_pass"] == 0.75


def test_not_measured_run_nulls_pass_rates() -> None:
    payload = null_unmeasured(asdict(EvalMetrics(test_outcome=TestOutcome(
        tests_pass=0.0, test_status="not_measured", tests_collected=0,
    ))))
    assert _outcome(payload)["tests_pass"] is None
    assert _outcome(payload)["functional_tests_pass"] is None


def test_measured_zero_pass_rate_is_kept() -> None:
    # A genuine 0% (tests ran, all failed) must stay 0.0 — only
    # "not measured" becomes null.
    payload = null_unmeasured(asdict(EvalMetrics(test_outcome=TestOutcome(
        tests_pass=0.0, test_status="ok", tests_collected=5,
    ))))
    assert _outcome(payload)["tests_pass"] == 0.0
