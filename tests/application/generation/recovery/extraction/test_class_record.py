"""Tests for ClassRecord: frozen deterministic AST-fact DTO."""

import dataclasses

import pytest

from squeaky_clean.application.generation.recovery.extraction.class_record import ClassRecord


def _record() -> ClassRecord:
    return ClassRecord(
        fqn="proj.domain.user.User",
        bases=("Base",),
        methods=("rename(new_name)",),
        fields=("name: str",),
        imports=("proj.domain.base.Base",),
        decorators=("dataclass",),
    )


def test_holds_all_six_fact_tuples_verbatim() -> None:
    record = _record()
    assert record.fqn == "proj.domain.user.User"
    assert record.bases == ("Base",)
    assert record.methods == ("rename(new_name)",)
    assert record.fields == ("name: str",)
    assert record.imports == ("proj.domain.base.Base",)
    assert record.decorators == ("dataclass",)


def test_is_frozen() -> None:
    with pytest.raises(dataclasses.FrozenInstanceError):
        _record().fqn = "other"  # type: ignore[misc]


def test_equality_is_by_value() -> None:
    assert _record() == _record()
