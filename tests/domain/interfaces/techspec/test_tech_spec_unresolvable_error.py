"""Tests for TechSpecUnresolvableError."""

import pytest

from squeaky_clean.domain.interfaces.techspec.tech_spec_unresolvable_error import (
    TechSpecUnresolvableError,
)


def test_is_a_runtime_error() -> None:
    assert issubclass(TechSpecUnresolvableError, RuntimeError)


def test_carries_triple_message() -> None:
    with pytest.raises(TechSpecUnresolvableError, match="blob_storage"):
        raise TechSpecUnresolvableError("no TechSpec for blob_storage/s3/v1")
