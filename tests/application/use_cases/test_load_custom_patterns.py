"""Tests for LoadCustomPatterns + CustomPatternManifest validation."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from squeaky_clean.application.dtos.custom_pattern_manifest import (
    CustomPatternManifestEntry,
)
from squeaky_clean.application.use_cases.load_custom_patterns import (
    CustomPatternManifestError,
    LoadCustomPatterns,
)


def test_loads_real_example(tmp_path: Path) -> None:
    real = (Path(__file__).resolve().parents[3]
            / "eval" / "custom_patterns"
            / "example_event_sourced_aggregate.json")
    manifest = LoadCustomPatterns().load(real)
    assert len(manifest.entries) == 1
    assert manifest.entries[0].name == "EventSourcedAggregate"
    assert manifest.extra_spec_roots == ("./eval/custom_patterns/specs/",)


def test_load_missing_path_raises(tmp_path: Path) -> None:
    with pytest.raises(CustomPatternManifestError):
        LoadCustomPatterns().load(tmp_path / "missing.json")


def test_load_invalid_json_raises(tmp_path: Path) -> None:
    p = tmp_path / "bad.json"
    p.write_text("{not json")
    with pytest.raises(CustomPatternManifestError):
        LoadCustomPatterns().load(p)


def test_load_non_object_top_level_raises(tmp_path: Path) -> None:
    p = tmp_path / "list.json"
    p.write_text(json.dumps([{"name": "X", "icp_spec_name": "Y"}]))
    with pytest.raises(CustomPatternManifestError):
        LoadCustomPatterns().load(p)


def test_load_patterns_not_list_raises(tmp_path: Path) -> None:
    p = tmp_path / "bad_shape.json"
    p.write_text(json.dumps({"patterns": "should be a list"}))
    with pytest.raises(CustomPatternManifestError):
        LoadCustomPatterns().load(p)


def test_entry_empty_name_raises() -> None:
    with pytest.raises(ValueError, match="name"):
        CustomPatternManifestEntry(name="", icp_spec_name="ok")


def test_entry_empty_icp_raises() -> None:
    with pytest.raises(ValueError, match="icp_spec_name"):
        CustomPatternManifestEntry(name="OK", icp_spec_name="")
