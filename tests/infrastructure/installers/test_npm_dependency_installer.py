"""Tests for NpmDependencyInstaller: success, npm absent, timeout."""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

from squeaky_clean.infrastructure.installers.npm_dependency_installer import (
    NpmDependencyInstaller,
)


def _ok(*_args: object, **_kwargs: object) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(["npm"], 0, "", "")


def test_skipped_when_no_package_json(tmp_path: Path) -> None:
    result = NpmDependencyInstaller().install(tmp_path)
    assert result.succeeded


def test_success_path(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text('{"name":"x"}')
    with patch(
        "squeaky_clean.infrastructure.installers.npm_dependency_installer.subprocess.run",
        side_effect=_ok,
    ):
        result = NpmDependencyInstaller().install(tmp_path)
    assert result.succeeded


def test_npm_absent(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text('{"name":"x"}')
    with patch(
        "squeaky_clean.infrastructure.installers.npm_dependency_installer.subprocess.run",
        side_effect=FileNotFoundError(),
    ):
        result = NpmDependencyInstaller().install(tmp_path)
    assert not result.succeeded
    assert "npm not available" in result.message


def test_npm_timeout(tmp_path: Path) -> None:
    (tmp_path / "package.json").write_text('{"name":"x"}')
    with patch(
        "squeaky_clean.infrastructure.installers.npm_dependency_installer.subprocess.run",
        side_effect=subprocess.TimeoutExpired(cmd="npm", timeout=300),
    ):
        result = NpmDependencyInstaller().install(tmp_path)
    assert not result.succeeded
    assert "timeout" in result.message
