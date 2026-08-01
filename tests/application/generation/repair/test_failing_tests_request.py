"""Tests for the FailingTestsRequest DTO."""

from pathlib import Path

import pytest

from squeaky_clean.application.generation.repair.failing_tests_request import (
    FailingTestsRequest,
)


def test_holds_fields_and_allows_missing_toolkit() -> None:
    req = FailingTestsRequest(
        raw_output="tests/test_x.py:3: TypeError",
        output_dir=Path("/tmp/proj"), toolkit=None,
    )
    assert req.raw_output.startswith("tests/")
    assert req.output_dir == Path("/tmp/proj")
    assert req.toolkit is None


def test_is_frozen() -> None:
    req = FailingTestsRequest(raw_output="", output_dir=Path("."), toolkit=None)
    with pytest.raises(AttributeError):
        req.raw_output = "x"  # type: ignore[misc]
