"""Tests for the Violation DTO."""

from dataclasses import FrozenInstanceError

import pytest

from squeaky_clean.application.dtos.violation import Violation


def test_violation_preserves_fields() -> None:
    v = Violation(
        rule_name="GranularityRule",
        file_path="/tmp/src/foo.py",
        message="file has 99 lines (>80)",
    )
    assert v.rule_name == "GranularityRule"
    assert "99 lines" in v.message


def test_violation_is_frozen() -> None:
    v = Violation(rule_name="R", file_path="/x.py", message="m")
    with pytest.raises(FrozenInstanceError):
        setattr(v, "rule_name", "Other")  # noqa: B010
