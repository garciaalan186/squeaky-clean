"""Tests for InfrastructureChoice DTO (H1)."""

import pytest

from squeaky_clean.application.dtos.infrastructure_choice import InfrastructureChoice


def test_infrastructure_choice_stores_triple() -> None:
    c = InfrastructureChoice(
        category="blob_storage", technology="local_disk", version_pin="stdlib",
    )
    assert c.category == "blob_storage"


def test_infrastructure_choice_rejects_empty_category() -> None:
    with pytest.raises(ValueError, match="category"):
        InfrastructureChoice(category="", technology="x", version_pin="1")


def test_infrastructure_choice_rejects_empty_technology() -> None:
    with pytest.raises(ValueError, match="technology"):
        InfrastructureChoice(category="x", technology="", version_pin="1")


def test_infrastructure_choice_rejects_empty_version_pin() -> None:
    with pytest.raises(ValueError, match="version_pin"):
        InfrastructureChoice(category="x", technology="y", version_pin="")
