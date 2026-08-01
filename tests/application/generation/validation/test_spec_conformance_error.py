"""Tests for SpecConformanceError."""

import pytest

from squeaky_clean.application.generation.validation.spec_conformance_error import (
    SpecConformanceError,
)


def test_is_a_value_error() -> None:
    assert issubclass(SpecConformanceError, ValueError)


def test_carries_violations_message() -> None:
    with pytest.raises(SpecConformanceError, match="semantics"):
        raise SpecConformanceError("architecture violates ProblemSpec semantics")
