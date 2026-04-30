"""Tests for the TestRunResult DTO."""

from dataclasses import FrozenInstanceError

import pytest

from squeaky_clean.application.dtos.test_run_result import TestRunResult


def test_test_run_result_preserves_fields() -> None:
    r = TestRunResult(
        passed=5, failed=1, errors=0, duration_ms=200, raw_output="5 passed"
    )
    assert r.passed == 5
    assert r.failed == 1
    assert r.duration_ms == 200


def test_test_run_result_is_frozen() -> None:
    r = TestRunResult(passed=0, failed=0, errors=0, duration_ms=0, raw_output="")
    with pytest.raises(FrozenInstanceError):
        setattr(r, "passed", 1)  # noqa: B010
