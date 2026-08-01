"""Tests for bracket_scanner (extracted from RewriteEntityConstruction)."""

from squeaky_clean.application.shared.language.bracket_scanner import (
    match_brace,
    split_top,
    top_index,
)


def test_match_brace_finds_balanced_close() -> None:
    text = "return { a: { b: 1 }, c: 2 } rest"
    close = match_brace(text, 7)
    assert text[close] == "}"
    assert text[7:close + 1] == "{ a: { b: 1 }, c: 2 }"


def test_match_brace_returns_minus_one_when_unbalanced() -> None:
    assert match_brace("return { a: {", 7) == -1


def test_split_top_ignores_nested_separators() -> None:
    assert split_top("a, f(b, c), {d, e}", ",") == ["a", " f(b, c)", " {d, e}"]


def test_top_index_skips_separators_inside_brackets() -> None:
    s = "make(x: 1): 2"
    assert top_index(s, ":") == len("make(x: 1)")


def test_top_index_returns_minus_one_when_only_nested() -> None:
    assert top_index("f(a: 1)", ":") == -1
