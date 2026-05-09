"""Tests for MavenDependencyInstaller: success, mvn absent, timeout."""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

from squeaky_clean.infrastructure.installers.maven_dependency_installer import (
    MavenDependencyInstaller,
)


def _ok(*_args: object, **_kwargs: object) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(["mvn"], 0, "", "")


def test_skipped_when_no_pom(tmp_path: Path) -> None:
    result = MavenDependencyInstaller().install(tmp_path)
    assert result.succeeded


def test_success_path(tmp_path: Path) -> None:
    (tmp_path / "pom.xml").write_text("<project/>")
    with patch(
        "squeaky_clean.infrastructure.installers.maven_dependency_installer.subprocess.run",
        side_effect=_ok,
    ):
        result = MavenDependencyInstaller().install(tmp_path)
    assert result.succeeded


def test_maven_absent(tmp_path: Path) -> None:
    (tmp_path / "pom.xml").write_text("<project/>")
    with patch(
        "squeaky_clean.infrastructure.installers.maven_dependency_installer.subprocess.run",
        side_effect=FileNotFoundError(),
    ):
        result = MavenDependencyInstaller().install(tmp_path)
    assert not result.succeeded
    assert "maven not available" in result.message


def test_maven_timeout(tmp_path: Path) -> None:
    (tmp_path / "pom.xml").write_text("<project/>")
    with patch(
        "squeaky_clean.infrastructure.installers.maven_dependency_installer.subprocess.run",
        side_effect=subprocess.TimeoutExpired(cmd="mvn", timeout=300),
    ):
        result = MavenDependencyInstaller().install(tmp_path)
    assert not result.succeeded
    assert "timeout" in result.message
