"""Tests for TechSpecResolutionError (reasoned resolution failure, R6.8)."""

import pytest

from squeaky_clean.domain.interfaces.techspec.tech_spec_resolution_error import (
    TechSpecResolutionError,
)
from squeaky_clean.domain.interfaces.techspec.tech_spec_unresolvable_error import (
    TechSpecUnresolvableError,
)


def test_subclasses_the_port_error() -> None:
    assert issubclass(TechSpecResolutionError, TechSpecUnresolvableError)


def test_carries_per_source_reasons() -> None:
    err = TechSpecResolutionError(
        "all sources failed", reasons=("fs: not found", "web: 503"),
    )
    assert err.reasons == ("fs: not found", "web: 503")


def test_reasons_default_to_empty() -> None:
    assert TechSpecResolutionError("boom").reasons == ()


def test_catchable_as_unresolvable() -> None:
    with pytest.raises(TechSpecUnresolvableError):
        raise TechSpecResolutionError("all sources failed")
