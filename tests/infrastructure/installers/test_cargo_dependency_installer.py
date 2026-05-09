"""Tests for CargoDependencyInstaller: success, cargo absent, timeout."""

from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

from squeaky_clean.infrastructure.installers.cargo_dependency_installer import (
    CargoDependencyInstaller,
)


def _ok(*_args: object, **_kwargs: object) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(["cargo"], 0, "", "")


def test_skipped_when_no_cargo_toml(tmp_path: Path) -> None:
    result = CargoDependencyInstaller().install(tmp_path)
    assert result.succeeded


def test_success_path(tmp_path: Path) -> None:
    (tmp_path / "Cargo.toml").write_text("[package]\nname=\"x\"\n")
    with patch(
        "squeaky_clean.infrastructure.installers.cargo_dependency_installer.subprocess.run",
        side_effect=_ok,
    ) as run:
        result = CargoDependencyInstaller().install(tmp_path)
    assert result.succeeded
    cmd = run.call_args[0][0]
    assert "--offline" not in cmd  # no Cargo.lock present


def test_cargo_uses_offline_when_lockfile_present(tmp_path: Path) -> None:
    (tmp_path / "Cargo.toml").write_text("[package]\n")
    (tmp_path / "Cargo.lock").write_text("# lock\n")
    with patch(
        "squeaky_clean.infrastructure.installers.cargo_dependency_installer.subprocess.run",
        side_effect=_ok,
    ) as run:
        CargoDependencyInstaller().install(tmp_path)
    assert "--offline" in run.call_args[0][0]


def test_cargo_absent(tmp_path: Path) -> None:
    (tmp_path / "Cargo.toml").write_text("[package]\n")
    with patch(
        "squeaky_clean.infrastructure.installers.cargo_dependency_installer.subprocess.run",
        side_effect=FileNotFoundError(),
    ):
        result = CargoDependencyInstaller().install(tmp_path)
    assert not result.succeeded
    assert "cargo not available" in result.message


def test_cargo_timeout(tmp_path: Path) -> None:
    (tmp_path / "Cargo.toml").write_text("[package]\n")
    with patch(
        "squeaky_clean.infrastructure.installers.cargo_dependency_installer.subprocess.run",
        side_effect=subprocess.TimeoutExpired(cmd="cargo", timeout=600),
    ):
        result = CargoDependencyInstaller().install(tmp_path)
    assert not result.succeeded
    assert "timeout" in result.message
