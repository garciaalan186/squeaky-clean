"""Tests for LoadProblemSpecFromFile parsing produces/consumes contracts."""

import json
from pathlib import Path

from squeaky_clean.application.use_cases.load_problem_spec_from_file import (
    LoadProblemSpecFromFile,
)


def _write(tmp: Path, payload: dict[str, object]) -> Path:
    path = tmp / "problem.json"
    path.write_text(json.dumps(payload))
    return path


def test_load_parses_produces_and_consumes(tmp_path: Path) -> None:
    payload = {
        "id": "X", "tier": 0, "slug": "x", "description": "d",
        "required_bounded_contexts": ["x"], "acceptance_criteria": ["a"],
        "expected_module_count": [1, 1], "expected_class_count": [1, 1],
        "required_patterns": ["Entity"], "target_language": "python",
        "produces_contracts": [{
            "name": "events.raw", "transport": "kafka:events.raw",
            "fields": [
                {"name": "id", "type": "str"},
                {"name": "payload", "type": "str", "required": True},
            ],
        }],
        "consumes_contracts": [
            {"contract_name": "ledger.entries", "role": "consumes"},
        ],
    }
    spec = LoadProblemSpecFromFile().load(_write(tmp_path, payload))
    assert len(spec.produces_contracts) == 1
    assert spec.produces_contracts[0].name == "events.raw"
    assert {f.name for f in spec.produces_contracts[0].fields} == {
        "id", "payload",
    }
    assert len(spec.consumes_contracts) == 1
    assert spec.consumes_contracts[0].contract_name == "ledger.entries"
    assert spec.consumes_contracts[0].role == "consumes"


def test_load_defaults_contracts_to_empty(tmp_path: Path) -> None:
    payload = {
        "id": "X", "tier": 0, "slug": "x", "description": "d",
        "required_bounded_contexts": ["x"], "acceptance_criteria": ["a"],
        "expected_module_count": [1, 1], "expected_class_count": [1, 1],
        "required_patterns": ["Entity"], "target_language": "python",
    }
    spec = LoadProblemSpecFromFile().load(_write(tmp_path, payload))
    assert spec.produces_contracts == ()
    assert spec.consumes_contracts == ()
