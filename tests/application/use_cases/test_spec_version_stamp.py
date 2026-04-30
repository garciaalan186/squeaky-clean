"""Unit tests for SpecVersionStamp."""

from pathlib import Path

from squeaky_clean.application.use_cases.spec_version_stamp import SpecVersionStamp


def test_reads_explicit_version(tmp_path: Path) -> None:
    (tmp_path / "VERSION").write_text("1.2.3\n")
    assert SpecVersionStamp(tmp_path).version() == "1.2.3"


def test_missing_version_file_returns_default(tmp_path: Path) -> None:
    assert "unversioned" in SpecVersionStamp(tmp_path).version()
