"""Tests for MCDARegistry (H3)."""

import json
from pathlib import Path

import pytest

from squeaky_clean.application.use_cases.mcda_registry import (
    MCDARegistry,
    MCDARegistryEntryMissingError,
)

_REPO_ROOT = Path(__file__).resolve().parents[3]
_SCORES_ROOT = _REPO_ROOT / "eval" / "mcda_scores"


def test_registry_loads_bundled_blob_storage() -> None:
    candidates = MCDARegistry(_SCORES_ROOT).candidates("blob_storage")
    techs = {c.technology for c in candidates}
    assert techs >= {"local_disk", "s3", "azure_blob"}


def test_registry_raises_for_unknown_category() -> None:
    with pytest.raises(MCDARegistryEntryMissingError, match="bogus"):
        MCDARegistry(_SCORES_ROOT).candidates("bogus")


def test_registry_parses_scores_and_stability(tmp_path: Path) -> None:
    payload = {
        "category": "kv_cache",
        "candidates": [
            {"technology": "redis", "version_pin": "redis-py==5.0",
             "stability": "ga",
             "scores": {"ops": 4, "cost": 4, "cold": 4, "thru": 5,
                        "eco": 5, "reg": 5, "lic": 4, "team": 4}},
        ],
    }
    (tmp_path / "kv_cache.json").write_text(json.dumps(payload))
    candidates = MCDARegistry(tmp_path).candidates("kv_cache")
    assert len(candidates) == 1
    assert candidates[0].technology == "redis"
    assert candidates[0].stability == "ga"
    assert candidates[0].scores["thru"] == 5
