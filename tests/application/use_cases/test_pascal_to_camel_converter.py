"""Tests for PascalToCamelConverter."""

from squeaky_clean.application.use_cases.pascal_to_camel_converter import (
    PascalToCamelConverter,
)


def test_pascal_case_basic() -> None:
    assert PascalToCamelConverter().convert("TodoRepository") == "todoRepository"


def test_single_word() -> None:
    assert PascalToCamelConverter().convert("Calculator") == "calculator"


def test_already_camel_is_idempotent() -> None:
    assert PascalToCamelConverter().convert("todoRepository") == "todoRepository"


def test_empty_string() -> None:
    assert PascalToCamelConverter().convert("") == ""


def test_single_char() -> None:
    assert PascalToCamelConverter().convert("A") == "a"


def test_leading_acronym() -> None:
    assert PascalToCamelConverter().convert("HTTPClient") == "httpClient"


def test_all_upper_abbrev() -> None:
    assert PascalToCamelConverter().convert("HTTP") == "http"
