"""Tests for TechSpecFetchFailed (R6.8 outcome union)."""

import dataclasses

import pytest

from squeaky_clean.domain.value_objects.tech_spec_fetch_failed import TechSpecFetchFailed


def test_carries_reason() -> None:
    failed = TechSpecFetchFailed("http 503 from docs host")
    assert failed.reason == "http 503 from docs host"


def test_frozen() -> None:
    failed = TechSpecFetchFailed("x")
    with pytest.raises(dataclasses.FrozenInstanceError):
        failed.reason = "y"  # type: ignore[misc]


def test_equality_by_value() -> None:
    assert TechSpecFetchFailed("same") == TechSpecFetchFailed("same")
    assert TechSpecFetchFailed("a") != TechSpecFetchFailed("b")
