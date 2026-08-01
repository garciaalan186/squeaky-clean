"""Tests for PythonIntegrationBootstrap: package inits + conftest skeleton files."""

from pathlib import Path

from squeaky_clean.application.generation.integration.bootstrap.python_integration_bootstrap import (
    PythonIntegrationBootstrap,
)
from squeaky_clean.domain.interfaces.integration_bootstrap import IntegrationBootstrap
from squeaky_clean.domain.interfaces.project_file_system import ProjectFileSystem


class _RecordingFileSystem(ProjectFileSystem):
    """In-memory fake capturing every write as path -> content."""

    def __init__(self) -> None:
        self.files: dict[Path, str] = {}

    def read(self, path: Path) -> str:
        return self.files[path]

    def write(self, path: Path, content: str) -> None:
        self.files[path] = content

    def list_files(self, root: Path) -> list[Path]:
        return sorted(p for p in self.files if root in p.parents)


def test_seeds_root_and_all_layer_package_inits(tmp_path: Path) -> None:
    fs = _RecordingFileSystem()
    PythonIntegrationBootstrap(fs).bootstrap(tmp_path)
    assert fs.files[tmp_path / "src" / "__init__.py"] == ""
    assert fs.files[tmp_path / "tests" / "__init__.py"] == ""
    for layer in ("domain", "application", "infrastructure", "interface"):
        assert fs.files[tmp_path / "src" / layer / "__init__.py"] == ""
        assert fs.files[tmp_path / "tests" / layer / "__init__.py"] == ""


def test_conftest_injects_project_root_onto_sys_path(tmp_path: Path) -> None:
    fs = _RecordingFileSystem()
    PythonIntegrationBootstrap(fs).bootstrap(tmp_path)
    conftest = fs.files[tmp_path / "tests" / "conftest.py"]
    assert "sys.path.insert(0, str(_ROOT))" in conftest
    assert "Path(__file__).resolve().parent.parent" in conftest


def test_writes_exactly_eleven_skeleton_files(tmp_path: Path) -> None:
    fs = _RecordingFileSystem()
    bootstrap = PythonIntegrationBootstrap(fs)
    assert isinstance(bootstrap, IntegrationBootstrap)
    bootstrap.bootstrap(tmp_path)
    # 2 root inits + 4 layers x 2 trees + conftest.py
    assert len(fs.files) == 11
