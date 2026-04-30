"""Tests for the RetryPolicy DTO."""

import pytest

from squeaky_clean.application.dtos.retry_policy import RetryPolicy


def test_defaults_are_valid() -> None:
    p = RetryPolicy()
    assert p.max_icp_retries == 1
    assert p.max_fixer_passes == 1
    assert p.backoff_base_seconds == 1.0
    assert p.backoff_multiplier == 2.0


def test_zero_retries_is_legal() -> None:
    p = RetryPolicy(max_icp_retries=0, max_fixer_passes=0)
    assert p.max_icp_retries == 0


def test_negative_max_icp_retries_rejected() -> None:
    with pytest.raises(ValueError):
        RetryPolicy(max_icp_retries=-1)


def test_negative_max_fixer_passes_rejected() -> None:
    with pytest.raises(ValueError):
        RetryPolicy(max_fixer_passes=-1)


def test_negative_backoff_base_rejected() -> None:
    with pytest.raises(ValueError):
        RetryPolicy(backoff_base_seconds=-0.1)


def test_multiplier_below_one_rejected() -> None:
    with pytest.raises(ValueError):
        RetryPolicy(backoff_multiplier=0.99)


def test_delay_for_grows_exponentially() -> None:
    p = RetryPolicy(backoff_base_seconds=2.0, backoff_multiplier=3.0)
    assert p.delay_for(0) == 2.0
    assert p.delay_for(1) == 6.0
    assert p.delay_for(2) == 18.0


def test_delay_for_negative_attempt_returns_zero() -> None:
    p = RetryPolicy()
    assert p.delay_for(-1) == 0.0
