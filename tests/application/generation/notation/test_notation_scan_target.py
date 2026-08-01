"""Tests for NotationScanTarget value object."""

import dataclasses

import pytest

from squeaky_clean.application.generation.notation.notation_scan_target import (
    NotationScanTarget,
)


def test_carries_text_and_delimiters() -> None:
    target = NotationScanTarget("{body}", "{", "}")
    assert target.text == "{body}"
    assert target.opener == "{"
    assert target.closer == "}"


def test_is_frozen() -> None:
    target = NotationScanTarget("x", "[", "]")
    with pytest.raises(dataclasses.FrozenInstanceError):
        target.text = "y"  # type: ignore[misc]
