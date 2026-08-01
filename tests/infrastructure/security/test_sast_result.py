"""Tests for the SASTResult value object."""

import pytest

from squeaky_clean.infrastructure.security.sast_result import SASTResult


def test_holds_run_summary() -> None:
    r = SASTResult(tool="bandit", available=True, issues=2, raw_output=">> x\n>> y")
    assert r.tool == "bandit"
    assert r.available is True
    assert r.issues == 2


def test_is_frozen() -> None:
    r = SASTResult(tool="semgrep", available=False, issues=0, raw_output="")
    with pytest.raises(AttributeError):
        r.issues = 5  # type: ignore[misc]
