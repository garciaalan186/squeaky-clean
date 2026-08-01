"""Tests for the TechSpecTarget value object."""

import pytest

from squeaky_clean.domain.value_objects.tech_spec_target import TechSpecTarget


def test_holds_the_choice_triple() -> None:
    t = TechSpecTarget(category="blob_storage", technology="s3",
                       version_pin="boto3==1.40")
    assert t.category == "blob_storage"
    assert t.technology == "s3"
    assert t.version_pin == "boto3==1.40"


def test_is_frozen() -> None:
    t = TechSpecTarget(category="c", technology="t", version_pin="v")
    with pytest.raises(AttributeError):
        t.technology = "other"  # type: ignore[misc]
