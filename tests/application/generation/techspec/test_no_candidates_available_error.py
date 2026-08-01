"""Tests for NoCandidatesAvailableError."""

import pytest

from squeaky_clean.application.generation.techspec.no_candidates_available_error import (
    NoCandidatesAvailableError,
)


def test_is_a_lookup_error() -> None:
    assert issubclass(NoCandidatesAvailableError, LookupError)


def test_carries_category() -> None:
    with pytest.raises(NoCandidatesAvailableError, match="blob_storage"):
        raise NoCandidatesAvailableError("blob_storage")
