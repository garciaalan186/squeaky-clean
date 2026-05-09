"""PipDependencyInstaller: shells out to pip to install requirements.txt deps."""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

from squeaky_clean.application.dtos.install_result import InstallResult
from squeaky_clean.domain.interfaces.dependency_installer import DependencyInstaller
from squeaky_clean.infrastructure.observability.json_logger import JSONLogger

_TIMEOUT_SECONDS: int = 300
_MAX_OUTPUT: int = 4000


class PipDependencyInstaller(DependencyInstaller):
    """Runs ``pip install -r requirements.txt --target .test-deps/``."""

    def __init__(self) -> None:
        self._logger: JSONLogger = JSONLogger()

    def install(self, project_dir: Path) -> InstallResult:
        """Install Python deps from ``<project_dir>/requirements.txt``.

        Skips silently when no requirements.txt exists. 5-minute
        timeout. Best-effort: returns failed (never raises) on missing
        pip / timeout.
        """
        req = project_dir / "requirements.txt"
        if not req.is_file():
            return InstallResult(True, 0, "no requirements.txt; skipped")
        target = project_dir / ".test-deps"
        cmd = [sys.executable, "-m", "pip", "install", "-r",
               str(req), "--target", str(target), "--quiet"]
        start = time.monotonic()
        try:
            completed = subprocess.run(
                cmd, cwd=str(project_dir), capture_output=True, text=True,
                timeout=_TIMEOUT_SECONDS, check=False,
            )
        except FileNotFoundError:
            self._logger.event("pip_not_available", project=str(project_dir))
            return InstallResult(False, 0, "pip not available")
        except subprocess.TimeoutExpired:
            self._logger.event("pip_timeout", project=str(project_dir))
            elapsed = int((time.monotonic() - start) * 1000)
            return InstallResult(False, elapsed, "pip timeout")
        elapsed = int((time.monotonic() - start) * 1000)
        out = (completed.stdout + completed.stderr)[:_MAX_OUTPUT]
        ok = completed.returncode == 0
        return InstallResult(ok, elapsed, "ok" if ok else out)
