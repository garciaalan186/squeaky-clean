"""Tests for the IntegrationResult DTO."""

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from squeaky_clean.application.dtos.integration_result import IntegrationResult


def test_integration_result_preserves_fields() -> None:
    result = IntegrationResult(
        output_dir=Path("/tmp/out"),
        files_written=(Path("/tmp/out/src/foo.py"),),
        test_files_written=(Path("/tmp/out/tests/foo_test.py"),),
    )
    assert result.output_dir == Path("/tmp/out")
    assert len(result.files_written) == 1
    assert len(result.test_files_written) == 1


def test_integration_result_is_frozen() -> None:
    result = IntegrationResult(
        output_dir=Path("/tmp/out"),
        files_written=(),
        test_files_written=(),
    )
    with pytest.raises(FrozenInstanceError):
        setattr(result, "output_dir", Path("/other"))  # noqa: B010
