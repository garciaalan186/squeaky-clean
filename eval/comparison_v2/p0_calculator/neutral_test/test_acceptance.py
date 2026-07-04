"""Neutral acceptance tests for P0 Calculator.

Each test maps to one acceptance criterion in problem.json. Tests use only
the `calc` fixture from conftest.py — no system-specific imports.
"""
from __future__ import annotations

import pytest


def test_add_2_3_eq_5(calc) -> None:
    assert calc["add"](2, 3) == 5


def test_subtract_5_2_eq_3(calc) -> None:
    assert calc["subtract"](5, 2) == 3


def test_multiply_4_3_eq_12(calc) -> None:
    assert calc["multiply"](4, 3) == 12


def test_divide_10_2_eq_5(calc) -> None:
    assert calc["divide"](10, 2) == 5


def test_divide_by_zero_raises(calc) -> None:
    divide = calc["divide"]
    with pytest.raises(Exception):
        divide(1, 0)
