"""Tests for TechSpecPoisoned (R6.8 outcome union)."""

import dataclasses

import pytest

from squeaky_clean.domain.value_objects.tech_spec_fetch_failed import TechSpecFetchFailed
from squeaky_clean.domain.value_objects.tech_spec_poisoned import TechSpecPoisoned


def test_carries_reason() -> None:
    poisoned = TechSpecPoisoned("prompt-injection marker matched")
    assert poisoned.reason == "prompt-injection marker matched"


def test_frozen() -> None:
    poisoned = TechSpecPoisoned("x")
    with pytest.raises(dataclasses.FrozenInstanceError):
        poisoned.reason = "y"  # type: ignore[misc]


def test_distinct_from_fetch_failed() -> None:
    # A security rejection must never compare equal to an availability error.
    poisoned: object = TechSpecPoisoned("r")
    failed: object = TechSpecFetchFailed("r")
    assert poisoned != failed
