"""Tests for UnknownConventionError."""

import pytest

from squeaky_clean.application.generation.notation.unknown_convention_error import (
    UnknownConventionError,
)


def test_is_a_value_error() -> None:
    assert issubclass(UnknownConventionError, ValueError)


def test_carries_message() -> None:
    with pytest.raises(UnknownConventionError, match="bad_tag"):
        raise UnknownConventionError("unknown domain convention tag: bad_tag")
