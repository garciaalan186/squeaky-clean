"""Boundary tests for LoadProblemSpecFromFile pattern validation (R6.6b)."""

import json
from pathlib import Path

import pytest

from squeaky_clean.application.shared.problem.load_problem_spec_from_file import (
    LoadProblemSpecFromFile,
)


def _write(tmp_path: Path, patterns: list[str]) -> Path:
    payload = {
        "id": "PX", "tier": 0, "slug": "s", "description": "d",
        "expected_module_count": [1, 1], "expected_class_count": [1, 1],
        "required_patterns": patterns,
    }
    path = tmp_path / "spec.json"
    path.write_text(json.dumps(payload))
    return path


def test_catalog_pattern_names_load(tmp_path: Path) -> None:
    spec = LoadProblemSpecFromFile().load(
        _write(tmp_path, ["Entity", "ValueObject"]),
    )
    assert spec.required_patterns == ["Entity", "ValueObject"]


def test_unknown_pattern_name_rejected_at_boundary(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="unknown pattern: 'NotAPattern'"):
        LoadProblemSpecFromFile().load(_write(tmp_path, ["NotAPattern"]))
