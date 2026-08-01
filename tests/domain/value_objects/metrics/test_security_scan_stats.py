"""Tests for the SecurityScanStats value object."""

import dataclasses

import pytest

from squeaky_clean.domain.value_objects.metrics.security_scan_stats import SecurityScanStats


def test_defaults_are_zero() -> None:
    s = SecurityScanStats()
    assert s.secret_leaks_detected == 0
    assert s.sast_high_findings == 0
    assert s.sast_medium_findings == 0
    assert s.sast_failed is False


def test_is_frozen() -> None:
    s = SecurityScanStats()
    with pytest.raises(dataclasses.FrozenInstanceError):
        s.sast_failed = True  # type: ignore[misc]


def test_holds_scan_findings() -> None:
    s = SecurityScanStats(
        secret_leaks_detected=1, sast_high_findings=2,
        sast_medium_findings=3, sast_failed=True,
    )
    assert s.secret_leaks_detected == 1
    assert s.sast_high_findings == 2
    assert s.sast_failed is True
