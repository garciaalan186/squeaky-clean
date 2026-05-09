"""GoDependencyInstaller: runs `go mod download` then `go mod tidy`."""

from __future__ import annotations

import subprocess
import time
from pathlib import Path

from squeaky_clean.application.dtos.install_result import InstallResult
from squeaky_clean.domain.interfaces.dependency_installer import DependencyInstaller
from squeaky_clean.infrastructure.observability.json_logger import JSONLogger

_TIMEOUT_SECONDS: int = 300
_MAX_OUTPUT: int = 4000


class GoDependencyInstaller(DependencyInstaller):
    """Runs ``go mod download`` then ``go mod tidy`` for Go projects."""

    def __init__(self) -> None:
        self._logger: JSONLogger = JSONLogger()

    def install(self, project_dir: Path) -> InstallResult:
        """Resolve and tidy Go modules; best-effort on toolchain absent."""
        if not (project_dir / "go.mod").is_file():
            return InstallResult(True, 0, "no go.mod; skipped")
        start = time.monotonic()
        for cmd in (["go", "mod", "download"], ["go", "mod", "tidy"]):
            try:
                completed = subprocess.run(
                    cmd, cwd=str(project_dir), capture_output=True, text=True,
                    timeout=_TIMEOUT_SECONDS, check=False,
                )
            except FileNotFoundError:
                self._logger.event("go_not_available", project=str(project_dir))
                return InstallResult(False, 0, "go not available")
            except subprocess.TimeoutExpired:
                self._logger.event("go_timeout", project=str(project_dir))
                elapsed = int((time.monotonic() - start) * 1000)
                return InstallResult(False, elapsed, "go timeout")
            if completed.returncode != 0:
                elapsed = int((time.monotonic() - start) * 1000)
                out = (completed.stdout + completed.stderr)[:_MAX_OUTPUT]
                return InstallResult(False, elapsed, out)
        elapsed = int((time.monotonic() - start) * 1000)
        return InstallResult(True, elapsed, "ok")
