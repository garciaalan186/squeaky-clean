"""Tests for TypeScriptIntegrationBootstrap."""

import json
from pathlib import Path

from squeaky_clean.application.use_cases.typescript_integration_bootstrap import (
    TypeScriptIntegrationBootstrap,
)
from squeaky_clean.infrastructure.filesystem.local_file_system import LocalFileSystem


def test_bootstrap_writes_package_json(tmp_path: Path) -> None:
    TypeScriptIntegrationBootstrap(LocalFileSystem()).bootstrap(tmp_path)
    pkg = tmp_path / "package.json"
    assert pkg.exists()
    data = json.loads(pkg.read_text())
    assert data["type"] == "module"
    assert "typescript" in data["devDependencies"]


def test_bootstrap_writes_tsconfig_json(tmp_path: Path) -> None:
    TypeScriptIntegrationBootstrap(LocalFileSystem()).bootstrap(tmp_path)
    cfg = tmp_path / "tsconfig.json"
    assert cfg.exists()
    data = json.loads(cfg.read_text())
    assert data["compilerOptions"]["module"] == "nodenext"
    assert data["compilerOptions"]["strict"] is True
    assert data["compilerOptions"]["outDir"] == "dist"
