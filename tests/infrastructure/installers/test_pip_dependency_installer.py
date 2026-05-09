"""Tests for PipDependencyInstaller: success, missing pip, timeout."""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

from squeaky_clean.infrastructure.installers.pip_dependency_installer import (
    PipDependencyInstaller,
)


def _ok(*_args: object, **_kwargs: object) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(["pip"], 0, "", "")


def _fail(*_args: object, **_kwargs: object) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(["pip"], 1, "", "boom")


def test_skipped_when_no_requirements(tmp_path: Path) -> None:
    result = PipDependencyInstaller().install(tmp_path)
    assert result.succeeded
    assert "skipped" in result.message


def test_success_path(tmp_path: Path) -> None:
    (tmp_path / "requirements.txt").write_text("six==1.16\n")
    with patch(
        "squeaky_clean.infrastructure.installers.pip_dependency_installer.subprocess.run",
        side_effect=_ok,
    ):
        result = PipDependencyInstaller().install(tmp_path)
    assert result.succeeded
    assert result.message == "ok"


def test_pip_not_available(tmp_path: Path) -> None:
    (tmp_path / "requirements.txt").write_text("six==1.16\n")
    with patch(
        "squeaky_clean.infrastructure.installers.pip_dependency_installer.subprocess.run",
        side_effect=FileNotFoundError(),
    ):
        result = PipDependencyInstaller().install(tmp_path)
    assert not result.succeeded
    assert "pip not available" in result.message


def test_pip_timeout(tmp_path: Path) -> None:
    (tmp_path / "requirements.txt").write_text("six==1.16\n")
    with patch(
        "squeaky_clean.infrastructure.installers.pip_dependency_installer.subprocess.run",
        side_effect=subprocess.TimeoutExpired(cmd="pip", timeout=300),
    ):
        result = PipDependencyInstaller().install(tmp_path)
    assert not result.succeeded
    assert "timeout" in result.message


def test_pip_nonzero_returns_failed(tmp_path: Path) -> None:
    (tmp_path / "requirements.txt").write_text("six==1.16\n")
    with patch(
        "squeaky_clean.infrastructure.installers.pip_dependency_installer.subprocess.run",
        side_effect=_fail,
    ):
        result = PipDependencyInstaller().install(tmp_path)
    assert not result.succeeded
    assert "boom" in result.message
