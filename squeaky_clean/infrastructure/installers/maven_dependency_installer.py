"""MavenDependencyInstaller: runs `mvn dependency:resolve` ahead of tests."""

from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path

from squeaky_clean.application.dtos.install_result import InstallResult
from squeaky_clean.domain.interfaces.dependency_installer import DependencyInstaller
from squeaky_clean.infrastructure.observability.json_logger import JSONLogger

_TIMEOUT_SECONDS: int = 300
_MAX_OUTPUT: int = 4000
_JDK_CANDIDATES: tuple[str, ...] = (
    "/usr/lib/jvm/java-11-openjdk-amd64",
    "/usr/lib/jvm/java-17-openjdk-amd64",
    "/usr/lib/jvm/java-21-openjdk-amd64",
    "/usr/lib/jvm/default-java",
)


def _resolve_java_home() -> str | None:
    existing = os.environ.get("JAVA_HOME")
    if existing and (Path(existing) / "bin" / "javac").is_file():
        return existing
    for c in _JDK_CANDIDATES:
        if (Path(c) / "bin" / "javac").is_file():
            return c
    return None


class MavenDependencyInstaller(DependencyInstaller):
    """Runs ``mvn -q dependency:resolve`` against a generated project."""

    def __init__(self) -> None:
        self._logger: JSONLogger = JSONLogger()

    def install(self, project_dir: Path) -> InstallResult:
        """Resolve declared Maven deps; best-effort on mvn absent/timeout."""
        if not (project_dir / "pom.xml").is_file():
            return InstallResult(True, 0, "no pom.xml; skipped")
        env = os.environ.copy()
        java_home = _resolve_java_home()
        if java_home is not None:
            env["JAVA_HOME"] = java_home
        start = time.monotonic()
        try:
            completed = subprocess.run(
                ["mvn", "-q", "dependency:resolve"], cwd=str(project_dir),
                capture_output=True, text=True, env=env,
                timeout=_TIMEOUT_SECONDS, check=False,
            )
        except FileNotFoundError:
            self._logger.event("mvn_not_available", project=str(project_dir))
            return InstallResult(False, 0, "maven not available")
        except subprocess.TimeoutExpired:
            self._logger.event("mvn_timeout", project=str(project_dir))
            elapsed = int((time.monotonic() - start) * 1000)
            return InstallResult(False, elapsed, "maven timeout")
        elapsed = int((time.monotonic() - start) * 1000)
        out = (completed.stdout + completed.stderr)[:_MAX_OUTPUT]
        ok = completed.returncode == 0
        return InstallResult(ok, elapsed, "ok" if ok else out)
