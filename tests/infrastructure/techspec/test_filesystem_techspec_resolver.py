"""Tests for FilesystemTechSpecResolver (H1)."""

import json
from pathlib import Path

import pytest

from squeaky_clean.domain.interfaces.tech_spec_resolver import TechSpecUnresolvableError
from squeaky_clean.infrastructure.techspec.filesystem_techspec_resolver import (
    FilesystemTechSpecResolver,
)
from squeaky_clean.infrastructure.techspec.jsonschema_techspec_validator import (
    JSONSchemaTechSpecValidator,
)

_REPO_ROOT = Path(__file__).resolve().parents[3]
_TECH_ROOT = _REPO_ROOT / "eval" / "tech_specs"
_SCHEMA = _TECH_ROOT / "_schema.v1.json"


def _resolver_at(root: Path) -> FilesystemTechSpecResolver:
    return FilesystemTechSpecResolver(
        root, JSONSchemaTechSpecValidator(_SCHEMA),
    )


def test_resolver_returns_local_disk_stdlib_techspec() -> None:
    spec = _resolver_at(_TECH_ROOT).resolve(
        "blob_storage", "local_disk", "stdlib",
    )
    assert spec.category == "blob_storage"
    assert spec.technology == "local_disk"
    assert spec.version_pin == "stdlib"
    assert spec.language == "python"
    assert {op.name for op in spec.primary_operations} == {
        "put_blob", "get_blob", "delete_blob",
    }


def test_resolver_raises_unresolvable_for_unknown_triple() -> None:
    with pytest.raises(TechSpecUnresolvableError):
        _resolver_at(_TECH_ROOT).resolve(
            "blob_storage", "fictional_tech", "v1",
        )


def test_resolver_falls_back_to_cache_when_bundled_missing(
    tmp_path: Path,
) -> None:
    bundled = json.loads(
        (_TECH_ROOT / "blob_storage" / "local_disk" / "stdlib.json").read_text()
    )
    cache_dir = tmp_path / ".cache" / "blob_storage" / "local_disk"
    cache_dir.mkdir(parents=True)
    (cache_dir / "stdlib.json").write_text(json.dumps(bundled))
    spec = _resolver_at(tmp_path).resolve(
        "blob_storage", "local_disk", "stdlib",
    )
    assert spec.technology == "local_disk"


def test_resolver_treats_schema_invalid_bundled_file_as_miss(
    tmp_path: Path,
) -> None:
    bad_dir = tmp_path / "blob_storage" / "broken"
    bad_dir.mkdir(parents=True)
    (bad_dir / "v1.json").write_text(
        json.dumps({"schema_version": "v1", "category": "blob_storage"})
    )
    with pytest.raises(TechSpecUnresolvableError):
        _resolver_at(tmp_path).resolve("blob_storage", "broken", "v1")


def test_resolver_rejects_mismatched_schema_version(tmp_path: Path) -> None:
    bundled = json.loads(
        (_TECH_ROOT / "blob_storage" / "local_disk" / "stdlib.json").read_text()
    )
    bundled["schema_version"] = "v2"
    target_dir = tmp_path / "blob_storage" / "local_disk"
    target_dir.mkdir(parents=True)
    (target_dir / "stdlib.json").write_text(json.dumps(bundled))
    with pytest.raises(TechSpecUnresolvableError):
        _resolver_at(tmp_path).resolve(
            "blob_storage", "local_disk", "stdlib",
        )
