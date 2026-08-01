"""Tests for NotationParseError."""

import pytest

from squeaky_clean.domain.entities.notation_parse_error import NotationParseError


def test_is_a_value_error() -> None:
    assert issubclass(NotationParseError, ValueError)


def test_carries_its_message() -> None:
    with pytest.raises(NotationParseError, match="missing MODULE"):
        raise NotationParseError("missing MODULE declaration")
