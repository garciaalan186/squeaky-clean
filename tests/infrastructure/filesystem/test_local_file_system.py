"""Tests for LocalFileSystem adapter."""

from pathlib import Path

from squeaky_clean.domain.interfaces.project_file_system import ProjectFileSystem
from squeaky_clean.infrastructure.filesystem.local_file_system import LocalFileSystem


def test_implements_port() -> None:
    assert isinstance(LocalFileSystem(), ProjectFileSystem)


def test_write_then_read_round_trip(tmp_path: Path) -> None:
    fs = LocalFileSystem()
    target = tmp_path / "sub" / "hello.py"
    fs.write(target, "class Hello:\n    ...\n")
    assert fs.read(target) == "class Hello:\n    ...\n"


def test_list_files_returns_every_file(tmp_path: Path) -> None:
    fs = LocalFileSystem()
    (tmp_path / "a.py").write_text("a")
    (tmp_path / "dir").mkdir()
    (tmp_path / "dir" / "b.py").write_text("b")
    listed = fs.list_files(tmp_path)
    names = sorted(p.name for p in listed)
    assert names == ["a.py", "b.py"]
