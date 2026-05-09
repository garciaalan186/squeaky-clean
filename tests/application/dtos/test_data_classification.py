"""Tests for DataClassification DTO."""

import pytest

from squeaky_clean.application.dtos.data_classification import DataClassification


def test_data_classification_round_trip() -> None:
    d = DataClassification(field_ref="User.password_hash", sensitivity="credential")
    assert d.field_ref == "User.password_hash"
    assert d.sensitivity == "credential"


def test_data_classification_rejects_unknown_sensitivity() -> None:
    with pytest.raises(ValueError, match="not in"):
        DataClassification(field_ref="X.y", sensitivity="bogus")


def test_data_classification_rejects_malformed_field_ref() -> None:
    with pytest.raises(ValueError, match="must look like"):
        DataClassification(field_ref="no_dot", sensitivity="public")


def test_data_classification_rejects_empty_segment() -> None:
    with pytest.raises(ValueError, match="must look like"):
        DataClassification(field_ref="User.", sensitivity="public")
