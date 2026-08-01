"""Tests for TechDocFormatUnknownError."""

import pytest

from squeaky_clean.application.generation.techspec.tech_doc_format_unknown_error import (
    TechDocFormatUnknownError,
)


def test_is_a_runtime_error() -> None:
    assert issubclass(TechDocFormatUnknownError, RuntimeError)


def test_carries_message() -> None:
    with pytest.raises(TechDocFormatUnknownError, match="no doc-site"):
        raise TechDocFormatUnknownError("no doc-site extractor matched")
