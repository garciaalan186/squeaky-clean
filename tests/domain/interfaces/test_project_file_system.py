"""Tests for ProjectFileSystem ABC."""

from pathlib import Path

import pytest

from squeaky_clean.domain.interfaces.project_file_system import ProjectFileSystem


class _StubFS(ProjectFileSystem):
    def read(self, path: Path) -> str:
        return str(path)

    def write(self, path: Path, content: str) -> None:
        return None

    def list_files(self, root: Path) -> list[Path]:
        return [root / "a.py"]


def test_project_file_system_cannot_be_instantiated_directly() -> None:
    with pytest.raises(TypeError):
        ProjectFileSystem()  # type: ignore[abstract]


def test_project_file_system_stub_round_trips() -> None:
    fs = _StubFS()
    assert fs.read(Path("/x")) == "/x"
    fs.write(Path("/x"), "body")
    assert fs.list_files(Path("/root")) == [Path("/root/a.py")]
