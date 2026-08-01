"""Tests for the SecretHit value object."""

from pathlib import Path

import pytest

from squeaky_clean.application.generation.security.secret_hit import SecretHit


def test_holds_location_and_label() -> None:
    hit = SecretHit(path=Path("src/config.py"), line=7, label="aws_access_key")
    assert hit.path == Path("src/config.py")
    assert hit.line == 7
    assert hit.label == "aws_access_key"


def test_is_frozen() -> None:
    hit = SecretHit(path=Path("x"), line=0, label="blocked_filename")
    with pytest.raises(AttributeError):
        hit.line = 3  # type: ignore[misc]
