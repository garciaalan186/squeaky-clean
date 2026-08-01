"""Tests for TechDocFetchError."""

import pytest

from squeaky_clean.domain.interfaces.techspec.tech_doc_fetch_error import (
    TechDocFetchError,
)


def test_is_a_runtime_error() -> None:
    assert issubclass(TechDocFetchError, RuntimeError)


def test_carries_url_message() -> None:
    with pytest.raises(TechDocFetchError, match="http"):
        raise TechDocFetchError("http://example.test returned 503")
