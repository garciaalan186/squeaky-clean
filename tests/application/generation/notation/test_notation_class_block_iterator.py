"""Tests for NotationClassBlockIterator entry iteration."""

import pytest

from squeaky_clean.application.generation.notation.notation_class_block_iterator import (
    NotationClassBlockIterator,
)
from squeaky_clean.domain.entities.notation_parse_error import NotationParseError


def test_yields_header_and_inner_per_entry() -> None:
    body = "A -> Entity {\n  fields: [id: Id]\n}\nB -> ValueObject {}"
    entries = list(NotationClassBlockIterator().iterate(body))
    assert [header for header, _ in entries] == ["A -> Entity", "B -> ValueObject"]
    assert "fields: [id: Id]" in entries[0][1]
    assert entries[1][1] == ""


def test_missing_brace_raises() -> None:
    with pytest.raises(NotationParseError, match="missing"):
        list(NotationClassBlockIterator().iterate("A -> Entity"))


def test_empty_body_yields_nothing() -> None:
    assert list(NotationClassBlockIterator().iterate("   \n  ")) == []
