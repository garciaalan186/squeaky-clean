"""Tests for the MCDARegistryEntry DTO."""

import pytest

from squeaky_clean.application.shared.mcda.mcda_registry_entry import MCDARegistryEntry


def test_holds_candidate_fields() -> None:
    e = MCDARegistryEntry(technology="s3", version_pin="boto3==1.40",
                          stability="ga", scores={"fit": 5})
    assert e.technology == "s3"
    assert e.scores == {"fit": 5}


def test_is_frozen() -> None:
    e = MCDARegistryEntry(technology="t", version_pin="v", stability="ga", scores={})
    with pytest.raises(AttributeError):
        e.stability = "beta"  # type: ignore[misc]
