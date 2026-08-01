"""Tests for CheckpointChecksum: stable hash of problem_id + spec library version."""

import hashlib
from pathlib import Path

from squeaky_clean.application.evaluation.eval.resume.checkpoint_checksum import (
    CheckpointChecksum,
)


def test_compute_hashes_problem_id_at_stamped_version(tmp_path: Path) -> None:
    (tmp_path / "VERSION").write_text("1.2.3\n")
    checksum = CheckpointChecksum(specs_root=tmp_path)
    expected = hashlib.sha256(b"P0@1.2.3").hexdigest()
    assert checksum.compute("P0") == expected


def test_missing_version_file_falls_back_to_unversioned_sentinel(tmp_path: Path) -> None:
    checksum = CheckpointChecksum(specs_root=tmp_path)
    expected = hashlib.sha256(b"P1@0.0.0+unversioned").hexdigest()
    assert checksum.compute("P1") == expected


def test_compute_is_deterministic_and_problem_sensitive(tmp_path: Path) -> None:
    (tmp_path / "VERSION").write_text("2.0.0")
    checksum = CheckpointChecksum(specs_root=tmp_path)
    assert checksum.compute("P0") == checksum.compute("P0")
    assert checksum.compute("P0") != checksum.compute("P1")


def test_spec_version_bump_invalidates_checksum(tmp_path: Path) -> None:
    (tmp_path / "VERSION").write_text("1.0.0")
    before = CheckpointChecksum(specs_root=tmp_path).compute("P0")
    (tmp_path / "VERSION").write_text("1.0.1")
    after = CheckpointChecksum(specs_root=tmp_path).compute("P0")
    assert before != after
