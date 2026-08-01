"""Tests for the TestOutcome value object."""

import dataclasses

import pytest

from squeaky_clean.domain.value_objects.metrics.test_outcome import TestOutcome


def test_defaults_are_zero_with_ok_status() -> None:
    t = TestOutcome()
    assert t.tests_pass == 0.0
    assert t.test_status == "ok"
    assert t.tests_collected == 0
    assert t.functional_test_count == 0
    assert t.security_test_count == 0


def test_is_frozen() -> None:
    t = TestOutcome()
    with pytest.raises(dataclasses.FrozenInstanceError):
        t.tests_pass = 1.0  # type: ignore[misc]


def test_holds_measured_values() -> None:
    t = TestOutcome(
        tests_pass=0.75, test_status="ok", tests_collected=4,
        functional_test_count=4, functional_tests_pass=0.75,
        security_test_count=2, security_tests_pass=0.5,
    )
    assert t.tests_pass == pytest.approx(0.75)
    assert t.security_tests_pass == pytest.approx(0.5)
