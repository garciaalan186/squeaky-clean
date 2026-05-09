"""Tests for GoDependencyInstaller: success, go absent, timeout."""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

from squeaky_clean.infrastructure.installers.go_dependency_installer import (
    GoDependencyInstaller,
)


def _ok(*_args: object, **_kwargs: object) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(["go"], 0, "", "")


def test_skipped_when_no_go_mod(tmp_path: Path) -> None:
    result = GoDependencyInstaller().install(tmp_path)
    assert result.succeeded


def test_success_path(tmp_path: Path) -> None:
    (tmp_path / "go.mod").write_text("module x\n")
    with patch(
        "squeaky_clean.infrastructure.installers.go_dependency_installer.subprocess.run",
        side_effect=_ok,
    ):
        result = GoDependencyInstaller().install(tmp_path)
    assert result.succeeded


def test_go_absent(tmp_path: Path) -> None:
    (tmp_path / "go.mod").write_text("module x\n")
    with patch(
        "squeaky_clean.infrastructure.installers.go_dependency_installer.subprocess.run",
        side_effect=FileNotFoundError(),
    ):
        result = GoDependencyInstaller().install(tmp_path)
    assert not result.succeeded
    assert "go not available" in result.message


def test_go_timeout(tmp_path: Path) -> None:
    (tmp_path / "go.mod").write_text("module x\n")
    with patch(
        "squeaky_clean.infrastructure.installers.go_dependency_installer.subprocess.run",
        side_effect=subprocess.TimeoutExpired(cmd="go", timeout=300),
    ):
        result = GoDependencyInstaller().install(tmp_path)
    assert not result.succeeded
    assert "timeout" in result.message
