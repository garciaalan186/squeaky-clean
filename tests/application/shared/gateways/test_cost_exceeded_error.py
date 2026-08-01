"""Tests for CostExceededError."""

import pytest

from squeaky_clean.application.shared.gateways.cost_exceeded_error import (
    CostExceededError,
)


def test_is_a_runtime_error() -> None:
    assert issubclass(CostExceededError, RuntimeError)


def test_carries_cap_message() -> None:
    with pytest.raises(CostExceededError, match="cost cap"):
        raise CostExceededError("cost cap $1.00 exceeded (spent $1.50)")
