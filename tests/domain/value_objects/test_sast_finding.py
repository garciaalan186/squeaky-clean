"""Tests for the SastFinding value object."""

import pytest

from squeaky_clean.domain.value_objects.sast_finding import SastFinding


def _finding() -> SastFinding:
    return SastFinding(severity="HIGH", confidence="MEDIUM", rule_id="B602",
                       file_path="src/shell.py", line=12, message="shell=True")


def test_holds_finding_fields() -> None:
    f = _finding()
    assert f.severity == "HIGH"
    assert f.confidence == "MEDIUM"
    assert f.rule_id == "B602"
    assert f.line == 12


def test_is_frozen() -> None:
    f = _finding()
    with pytest.raises(AttributeError):
        f.severity = "LOW"  # type: ignore[misc]
