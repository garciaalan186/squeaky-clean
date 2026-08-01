"""Tests for CustomPatternManifestError."""

import pytest

from squeaky_clean.application.shared.problem.custom_pattern_manifest_error import (
    CustomPatternManifestError,
)


def test_is_a_value_error() -> None:
    assert issubclass(CustomPatternManifestError, ValueError)


def test_carries_path_message() -> None:
    with pytest.raises(CustomPatternManifestError, match="manifest not found"):
        raise CustomPatternManifestError("manifest not found: /tmp/x.json")
