"""Tests for ImplementedClassParseError."""

import pytest

from squeaky_clean.application.generation.emission.parsers.implemented_class_parse_error import (
    ImplementedClassParseError,
)
from squeaky_clean.application.generation.emission.parsers.parse_implemented_class import (
    ParseImplementedClass,
)


def test_is_a_value_error_subclass() -> None:
    assert issubclass(ImplementedClassParseError, ValueError)


def test_message_round_trips_through_str() -> None:
    err = ImplementedClassParseError("code body does not declare class Foo")
    assert str(err) == "code body does not declare class Foo"


def test_catchable_as_plain_value_error() -> None:
    with pytest.raises(ValueError, match="no fenced block"):
        raise ImplementedClassParseError("no fenced block")


def test_raised_by_parser_on_unparseable_icp_output() -> None:
    with pytest.raises(ImplementedClassParseError):
        ParseImplementedClass().parse("prose without any code fence", "Foo")
