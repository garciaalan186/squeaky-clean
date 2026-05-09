"""Tests for TechSpec value object (H1)."""

import pytest

from squeaky_clean.application.dtos.tech_spec import TechSpec
from squeaky_clean.application.dtos.tech_spec_operation import TechSpecOperation


def _ops() -> tuple[TechSpecOperation, ...]:
    return (
        TechSpecOperation(
            name="put_blob",
            signature="(key: str, body: bytes) -> None",
            sdk_call="(self._root / key).write_bytes(body)",
            error_types=("OSError",),
            idempotency="idempotent",
        ),
    )


def _spec(**overrides: object) -> TechSpec:
    base: dict[str, object] = dict(
        schema_version="v1",
        category="blob_storage",
        technology="local_disk",
        version_pin="stdlib",
        language="python",
        install={"manager": "stdlib", "package": "pathlib"},
        imports={"primary": "from pathlib import Path"},
        client_construction={"code": "self._root = Path(root_dir)"},
        primary_operations=_ops(),
        auth={"method": "none"},
    )
    base.update(overrides)
    return TechSpec(**base)  # type: ignore[arg-type]


def test_techspec_round_trips_required_fields() -> None:
    s = _spec()
    assert s.category == "blob_storage"
    assert s.primary_operations[0].name == "put_blob"


def test_techspec_rejects_unknown_schema_version() -> None:
    with pytest.raises(ValueError, match="schema_version"):
        _spec(schema_version="v2")


def test_techspec_rejects_unknown_category() -> None:
    with pytest.raises(ValueError, match="category"):
        _spec(category="quantum_storage")


def test_techspec_rejects_unknown_language() -> None:
    with pytest.raises(ValueError, match="language"):
        _spec(language="cobol")


def test_techspec_rejects_empty_primary_operations() -> None:
    with pytest.raises(ValueError, match="primary_operations"):
        _spec(primary_operations=())


def test_techspec_operation_rejects_invalid_idempotency() -> None:
    with pytest.raises(ValueError, match="idempotency"):
        TechSpecOperation(
            name="x", signature="() -> None", sdk_call="pass",
            error_types=("OSError",), idempotency="maybe",
        )
