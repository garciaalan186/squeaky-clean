"""Tests for NotationListSplitter comma splitting."""

from squeaky_clean.application.generation.notation.notation_list_splitter import (
    NotationListSplitter,
)


def test_plain_tuple_splits_and_strips() -> None:
    assert NotationListSplitter().plain_tuple("[A, B, C]") == ("A", "B", "C")


def test_plain_tuple_honors_generic_brackets() -> None:
    result = NotationListSplitter().plain_tuple("[Map<K, V>, List<T>]")
    assert result == ("Map<K, V>", "List<T>")


def test_method_tuple_honors_parens() -> None:
    raw = "[pay(a: Money, b: Money): Result, refund(): void]"
    assert NotationListSplitter().method_tuple(raw) == (
        "pay(a: Money, b: Money): Result",
        "refund(): void",
    )


def test_empty_list_yields_empty_tuple() -> None:
    splitter = NotationListSplitter()
    assert splitter.plain_tuple("[]") == ()
    assert splitter.method_tuple("") == ()
