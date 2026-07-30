"""Tests for atomic_write_text (R0.9)."""

from pathlib import Path

import pytest

from squeaky_clean.application.shared.io.atomic_write import atomic_write_text


def test_writes_content_and_creates_parents(tmp_path: Path) -> None:
    target = tmp_path / "nested" / "dir" / "out.json"
    atomic_write_text(target, '{"a": 1}')
    assert target.read_text() == '{"a": 1}'


def test_replaces_existing_file(tmp_path: Path) -> None:
    target = tmp_path / "out.json"
    target.write_text("old")
    atomic_write_text(target, "new")
    assert target.read_text() == "new"


def test_interruption_leaves_old_file_not_partial(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    target = tmp_path / "out.json"
    target.write_text("original")

    import os as _os

    def _boom(_src: object, _dst: object) -> None:
        raise OSError("simulated crash during rename")

    monkeypatch.setattr(_os, "replace", _boom)
    with pytest.raises(OSError):
        atomic_write_text(target, "brand new content")

    # The reader sees the intact old file, never a truncated one.
    assert target.read_text() == "original"
    # And no temp litter is left behind.
    assert list(tmp_path.glob("*.tmp")) == []


def test_no_temp_files_left_on_success(tmp_path: Path) -> None:
    target = tmp_path / "out.json"
    atomic_write_text(target, "data")
    assert [p.name for p in tmp_path.iterdir()] == ["out.json"]
