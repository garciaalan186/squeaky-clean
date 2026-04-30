"""MavenTestRunner: shells out to `mvn test` and parses Surefire XML reports."""

from __future__ import annotations

import os
import subprocess
import time
import xml.etree.ElementTree as ET
from pathlib import Path

from squeaky_clean.application.dtos.test_run_result import TestRunResult
from squeaky_clean.infrastructure.observability.json_logger import JSONLogger
from squeaky_clean.infrastructure.testing.test_runner import TestRunner

_TIMEOUT_SECONDS: int = 300
_MAX_OUTPUT: int = 8000
# Candidate JDK locations probed when JAVA_HOME is unset. Maven needs a
# real JDK (with javac) — Ubuntu's default `java` may be a JRE-only path.
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
    for candidate in _JDK_CANDIDATES:
        if (Path(candidate) / "bin" / "javac").is_file():
            return candidate
    return None


class MavenTestRunner(TestRunner):
    """Runs ``mvn -q test`` against a project dir and parses Surefire XML."""

    def __init__(self, exclude_glob: str | None = None) -> None:
        self._exclude_glob: str | None = exclude_glob
        self._logger: JSONLogger = JSONLogger()

    def run(self, project_dir: Path) -> TestRunResult:
        """Invoke ``mvn -q test`` in ``project_dir`` and return a parsed result.

        Captures stdout+stderr combined, parses
        ``target/surefire-reports/TEST-*.xml`` for tests/failures/errors,
        and times the subprocess. 5-minute timeout. On Maven absent or
        timeout returns a zero-result and logs a warning.
        """
        start = time.monotonic()
        try:
            completed = self._invoke(project_dir)
        except FileNotFoundError:
            self._logger.event("mvn_not_available", project=str(project_dir))
            return TestRunResult(0, 0, 0, 0, "maven not available")
        except subprocess.TimeoutExpired:
            self._logger.event("mvn_timeout", project=str(project_dir))
            elapsed = int((time.monotonic() - start) * 1000)
            return TestRunResult(0, 0, 0, elapsed, "maven timeout")
        elapsed = int((time.monotonic() - start) * 1000)
        output = (completed.stdout + completed.stderr)[:_MAX_OUTPUT]
        return self._parse(project_dir, output, elapsed)

    def _invoke(self, project_dir: Path) -> subprocess.CompletedProcess[str]:
        cmd = ["mvn", "-q", "test"]
        if self._exclude_glob is not None:
            cmd.append(f"-Dtest=!{self._exclude_glob}")
        env = os.environ.copy()
        java_home = _resolve_java_home()
        if java_home is not None:
            env["JAVA_HOME"] = java_home
        return subprocess.run(
            cmd, cwd=str(project_dir), capture_output=True, text=True,
            timeout=_TIMEOUT_SECONDS, check=False, env=env,
        )

    def _parse(
        self, project_dir: Path, output: str, elapsed_ms: int,
    ) -> TestRunResult:
        reports_dir = project_dir / "target" / "surefire-reports"
        if not reports_dir.is_dir():
            return TestRunResult(0, 0, 0, elapsed_ms, output)
        total = failures = errors = 0
        for xml_path in reports_dir.glob("TEST-*.xml"):
            t, f, e = _parse_surefire_xml(xml_path)
            total += t
            failures += f
            errors += e
        passed = max(0, total - failures - errors)
        return TestRunResult(passed, failures, errors, elapsed_ms, output)


def _parse_surefire_xml(xml_path: Path) -> tuple[int, int, int]:
    """Return (tests, failures, errors) from one Surefire ``TEST-*.xml`` file."""
    try:
        root = ET.parse(xml_path).getroot()
    except (ET.ParseError, OSError):
        return 0, 0, 0
    return (
        int(root.get("tests", "0")),
        int(root.get("failures", "0")),
        int(root.get("errors", "0")),
    )
