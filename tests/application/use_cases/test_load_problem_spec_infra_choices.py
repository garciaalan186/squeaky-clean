"""Test that LoadProblemSpecFromFile parses infrastructure_choices (H1)."""

import json
from pathlib import Path

from squeaky_clean.application.use_cases.load_problem_spec_from_file import (
    LoadProblemSpecFromFile,
)


def test_infrastructure_choices_round_trip(tmp_path: Path) -> None:
    payload = {
        "id": "PX",
        "tier": 0,
        "slug": "blob-test",
        "description": "x",
        "expected_module_count": [1, 1],
        "expected_class_count": [1, 1],
        "infrastructure_choices": [
            {
                "category": "blob_storage",
                "technology": "local_disk",
                "version_pin": "stdlib",
            }
        ],
    }
    path = tmp_path / "spec.json"
    path.write_text(json.dumps(payload))
    spec = LoadProblemSpecFromFile().load(path)
    assert len(spec.infrastructure_choices) == 1
    c = spec.infrastructure_choices[0]
    assert c.category == "blob_storage"
    assert c.technology == "local_disk"
    assert c.version_pin == "stdlib"


def test_missing_infrastructure_choices_defaults_empty(tmp_path: Path) -> None:
    payload = {
        "id": "PY", "tier": 0, "slug": "no-infra", "description": "y",
        "expected_module_count": [1, 1], "expected_class_count": [1, 1],
    }
    path = tmp_path / "spec.json"
    path.write_text(json.dumps(payload))
    spec = LoadProblemSpecFromFile().load(path)
    assert spec.infrastructure_choices == ()
