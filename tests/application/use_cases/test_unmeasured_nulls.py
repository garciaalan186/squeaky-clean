"""Tests for unmeasured_nulls (R5.3: unmeasured != 0.0)."""

from dataclasses import asdict

from squeaky_clean.application.evaluation.eval.metrics.unmeasured_nulls import (
    null_unmeasured,
)
from squeaky_clean.domain.entities.eval_metrics import EvalMetrics


def test_security_score_nulled_when_no_security_tests() -> None:
    payload = null_unmeasured(asdict(EvalMetrics(
        security_tests_pass=0.0, security_test_count=0,
    )))
    assert payload["security_tests_pass"] is None


def test_measured_security_score_kept() -> None:
    payload = null_unmeasured(asdict(EvalMetrics(
        security_tests_pass=0.75, security_test_count=4,
    )))
    assert payload["security_tests_pass"] == 0.75


def test_not_measured_run_nulls_pass_rates() -> None:
    payload = null_unmeasured(asdict(EvalMetrics(
        tests_pass=0.0, test_status="not_measured", tests_collected=0,
    )))
    assert payload["tests_pass"] is None
    assert payload["functional_tests_pass"] is None


def test_measured_zero_pass_rate_is_kept() -> None:
    # A genuine 0% (tests ran, all failed) must stay 0.0 — only
    # "not measured" becomes null.
    payload = null_unmeasured(asdict(EvalMetrics(
        tests_pass=0.0, test_status="ok", tests_collected=5,
    )))
    assert payload["tests_pass"] == 0.0
