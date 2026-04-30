"""NpmDependencyInstaller: runs `npm install` for JS/TS projects."""

from __future__ import annotations

import subprocess
import time
from pathlib import Path

from squeaky_clean.application.dtos.install_result import InstallResult
from squeaky_clean.domain.interfaces.dependency_installer import DependencyInstaller
from squeaky_clean.infrastructure.observability.json_logger import JSONLogger

_TIMEOUT_SECONDS: int = 300
_MAX_OUTPUT: int = 4000


class NpmDependencyInstaller(DependencyInstaller):
    """Runs ``npm install --no-audit --no-fund --silent`` for a package.json."""

    def __init__(self) -> None:
        self._logger: JSONLogger = JSONLogger()

    def install(self, project_dir: Path) -> InstallResult:
        """Install npm deps; best-effort on npm absent / timeout."""
        if not (project_dir / "package.json").is_file():
            return InstallResult(True, 0, "no package.json; skipped")
        cmd = ["npm", "install", "--no-audit", "--no-fund", "--silent"]
        start = time.monotonic()
        try:
            completed = subprocess.run(
                cmd, cwd=str(project_dir), capture_output=True, text=True,
                timeout=_TIMEOUT_SECONDS, check=False,
            )
        except FileNotFoundError:
            self._logger.event("npm_not_available", project=str(project_dir))
            return InstallResult(False, 0, "npm not available")
        except subprocess.TimeoutExpired:
            self._logger.event("npm_timeout", project=str(project_dir))
            elapsed = int((time.monotonic() - start) * 1000)
            return InstallResult(False, elapsed, "npm timeout")
        elapsed = int((time.monotonic() - start) * 1000)
        out = (completed.stdout + completed.stderr)[:_MAX_OUTPUT]
        ok = completed.returncode == 0
        return InstallResult(ok, elapsed, "ok" if ok else out)
