"""CargoDependencyInstaller: runs `cargo build --tests` to fetch+compile deps."""

from __future__ import annotations

import subprocess
import time
from pathlib import Path

from squeaky_clean.application.dtos.install_result import InstallResult
from squeaky_clean.domain.interfaces.dependency_installer import DependencyInstaller
from squeaky_clean.infrastructure.observability.json_logger import JSONLogger

_TIMEOUT_SECONDS: int = 600
_MAX_OUTPUT: int = 4000


class CargoDependencyInstaller(DependencyInstaller):
    """Runs ``cargo build --tests`` to pre-fetch + compile crate deps."""

    def __init__(self) -> None:
        self._logger: JSONLogger = JSONLogger()

    def install(self, project_dir: Path) -> InstallResult:
        """Build test deps; uses ``--offline`` if Cargo.lock exists.

        Best-effort on cargo absent / 10-minute timeout.
        """
        if not (project_dir / "Cargo.toml").is_file():
            return InstallResult(True, 0, "no Cargo.toml; skipped")
        cmd = ["cargo", "build", "--tests"]
        if (project_dir / "Cargo.lock").is_file():
            cmd.append("--offline")
        start = time.monotonic()
        try:
            completed = subprocess.run(
                cmd, cwd=str(project_dir), capture_output=True, text=True,
                timeout=_TIMEOUT_SECONDS, check=False,
            )
        except FileNotFoundError:
            self._logger.event("cargo_not_available", project=str(project_dir))
            return InstallResult(False, 0, "cargo not available")
        except subprocess.TimeoutExpired:
            self._logger.event("cargo_timeout", project=str(project_dir))
            elapsed = int((time.monotonic() - start) * 1000)
            return InstallResult(False, elapsed, "cargo timeout")
        elapsed = int((time.monotonic() - start) * 1000)
        out = (completed.stdout + completed.stderr)[:_MAX_OUTPUT]
        ok = completed.returncode == 0
        return InstallResult(ok, elapsed, "ok" if ok else out)
