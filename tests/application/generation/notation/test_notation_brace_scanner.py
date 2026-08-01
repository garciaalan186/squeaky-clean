"""Tests for NotationBraceScanner balanced-region scanning."""

import pytest

from squeaky_clean.application.generation.notation.notation_brace_scanner import (
    NotationBraceScanner,
)
from squeaky_clean.domain.entities.notation_parse_error import NotationParseError


def test_inside_brace_handles_nesting() -> None:
    inner, end = NotationBraceScanner().inside_brace("{a {b} c} tail", 0)
    assert inner == "a {b} c"
    assert end == 9


def test_inside_bracket_returns_inner_text() -> None:
    inner, end = NotationBraceScanner().inside_bracket("[A, B]", 0)
    assert inner == "A, B"
    assert end == 6


def test_wrong_start_character_raises() -> None:
    with pytest.raises(NotationParseError, match="expected"):
        NotationBraceScanner().inside_brace("no brace here", 0)


def test_unbalanced_raises() -> None:
    with pytest.raises(NotationParseError, match="unbalanced"):
        NotationBraceScanner().inside_bracket("[never closed", 0)
