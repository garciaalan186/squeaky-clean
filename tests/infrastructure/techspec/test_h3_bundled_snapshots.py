"""Schema-validation tests for H3 bundled TechSpec snapshots."""

import json
from pathlib import Path

import pytest

from squeaky_clean.infrastructure.techspec.jsonschema_techspec_validator import (
    JSONSchemaTechSpecValidator,
)

_REPO_ROOT = Path(__file__).resolve().parents[3]
_TECH_ROOT = _REPO_ROOT / "eval" / "tech_specs"
_SCHEMA = _TECH_ROOT / "_schema.v1.json"


@pytest.mark.parametrize("relpath", [
    "blob_storage/local_disk/stdlib.json",
    "blob_storage/s3/boto3==1.34.json",
    "kv_cache/redis/redis-py==5.0.json",
    "rest_client/httpx/httpx==0.27.json",
])
def test_bundled_snapshot_validates(relpath: str) -> None:
    spec = json.loads((_TECH_ROOT / relpath).read_text())
    errors = JSONSchemaTechSpecValidator(_SCHEMA).validate(spec)
    assert errors == (), f"{relpath}: {errors}"
