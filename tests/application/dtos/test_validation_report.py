"""Tests for the ValidationReport DTO."""

from dataclasses import FrozenInstanceError

import pytest

from squeaky_clean.application.dtos.validation_report import ValidationReport
from squeaky_clean.application.dtos.violation import Violation


def test_validation_report_is_valid_when_empty() -> None:
    report = ValidationReport(violations=(), files_scanned=3)
    assert report.is_valid is True
    assert report.files_scanned == 3


def test_validation_report_is_invalid_with_violations() -> None:
    v = Violation(rule_name="R", file_path="/x.py", message="bad")
    report = ValidationReport(violations=(v,), files_scanned=1)
    assert report.is_valid is False
    assert len(report.violations) == 1


def test_validation_report_is_frozen() -> None:
    report = ValidationReport(violations=(), files_scanned=0)
    with pytest.raises(FrozenInstanceError):
        setattr(report, "files_scanned", 99)  # noqa: B010
