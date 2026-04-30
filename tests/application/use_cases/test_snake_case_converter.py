"""Tests for SnakeCaseConverter."""

from squeaky_clean.application.use_cases.snake_case_converter import SnakeCaseConverter


def test_pascal_case_basic() -> None:
    assert SnakeCaseConverter().convert("CalculatorService") == "calculator_service"


def test_mixed_digits() -> None:
    assert SnakeCaseConverter().convert("P0Calculator") == "p0_calculator"


def test_already_lower() -> None:
    assert SnakeCaseConverter().convert("operand") == "operand"


def test_single_word() -> None:
    assert SnakeCaseConverter().convert("Operand") == "operand"


def test_empty_string() -> None:
    assert SnakeCaseConverter().convert("") == ""


def test_consecutive_uppercase_abbrev() -> None:
    assert SnakeCaseConverter().convert("HTTPClient") == "http_client"


def test_trailing_digit() -> None:
    assert SnakeCaseConverter().convert("Version2") == "version2"
