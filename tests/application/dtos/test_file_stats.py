"""Tests for FileStats DTO."""

from dataclasses import FrozenInstanceError

import pytest

from squeaky_clean.application.dtos.file_stats import FileStats


def test_construction_preserves_fields() -> None:
    fs = FileStats(avg_line_count=12.5, max_line_count=40, orphan_count=2, artifact_char_count=500)
    assert fs.avg_line_count == 12.5
    assert fs.max_line_count == 40
    assert fs.orphan_count == 2
    assert fs.artifact_char_count == 500


def test_frozen_behavior() -> None:
    fs = FileStats(avg_line_count=0.0, max_line_count=0, orphan_count=0, artifact_char_count=0)
    with pytest.raises(FrozenInstanceError):
        fs.orphan_count = 5  # type: ignore[misc]
