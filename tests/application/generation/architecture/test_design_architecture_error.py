"""Tests for DesignArchitectureError: architect-failure error semantics."""

import pytest

from squeaky_clean.application.generation.architecture.design_architecture_error import (
    DesignArchitectureError,
)


def test_preserves_the_failure_message() -> None:
    err = DesignArchitectureError("architect returned no MODULE block")
    assert str(err) == "architect returned no MODULE block"


def test_is_catchable_as_runtime_error() -> None:
    with pytest.raises(RuntimeError, match="empty spec"):
        raise DesignArchitectureError("empty spec")


def test_is_a_distinct_runtime_error_subclass() -> None:
    assert issubclass(DesignArchitectureError, RuntimeError)
    assert DesignArchitectureError is not RuntimeError
