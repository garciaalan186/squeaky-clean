"""Tests for the SecurityConcern DTO."""

from dataclasses import FrozenInstanceError

import pytest

from squeaky_clean.application.dtos.security_concern import SecurityConcern


def test_security_concern_is_frozen() -> None:
    c = SecurityConcern(
        category="input_validation",
        target_class="Calculator",
        description="Empty string input not handled",
        test_scenario="Pass empty string and expect ValueError",
    )
    assert c.category == "input_validation"
    assert c.target_class == "Calculator"
    with pytest.raises(FrozenInstanceError):
        setattr(c, "category", "boundary")  # noqa: B010


def test_security_concern_fields() -> None:
    c = SecurityConcern(
        category="boundary",
        target_class="Operand",
        description="Negative values not checked",
        test_scenario="Pass -1 and verify behavior",
    )
    assert c.description == "Negative values not checked"
    assert c.test_scenario == "Pass -1 and verify behavior"
