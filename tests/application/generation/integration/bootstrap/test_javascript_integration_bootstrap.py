"""Tests for JavaScriptIntegrationBootstrap: minimal ES-module package.json."""

import json
from pathlib import Path

from squeaky_clean.application.generation.integration.bootstrap.javascript_integration_bootstrap import (  # noqa: E501
    JavaScriptIntegrationBootstrap,
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


def test_writes_package_json_marking_project_as_es_module(tmp_path: Path) -> None:
    fs = _RecordingFileSystem()
    JavaScriptIntegrationBootstrap(fs).bootstrap(tmp_path)
    body = fs.files[tmp_path / "package.json"]
    assert json.loads(body) == {"type": "module"}
    assert body.endswith("\n")


def test_writes_exactly_one_skeleton_file(tmp_path: Path) -> None:
    fs = _RecordingFileSystem()
    JavaScriptIntegrationBootstrap(fs).bootstrap(tmp_path)
    assert list(fs.files) == [tmp_path / "package.json"]


def test_implements_the_integration_bootstrap_port(tmp_path: Path) -> None:
    bootstrap = JavaScriptIntegrationBootstrap(_RecordingFileSystem())
    assert isinstance(bootstrap, IntegrationBootstrap)
    bootstrap.bootstrap(tmp_path)  # port contract: no return value, no raise
