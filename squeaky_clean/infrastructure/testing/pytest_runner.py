"""PytestRunner: shells out to pytest and parses the summary line."""

import re
import subprocess
import sys
import time
from pathlib import Path

from squeaky_clean.application.dtos.test_run_result import TestRunResult
from squeaky_clean.infrastructure.testing.test_runner import TestRunner

_TIMEOUT_SECONDS: int = 60
_PASSED: re.Pattern[str] = re.compile(r"(\d+) passed")
_FAILED: re.Pattern[str] = re.compile(r"(\d+) failed")
_ERRORS: re.Pattern[str] = re.compile(r"(\d+) error")


class PytestRunner(TestRunner):
    """Runs ``python -m pytest`` against a project dir and parses the summary."""

    def __init__(self, exclude_glob: str | None = None) -> None:
        self._exclude_glob: str | None = exclude_glob

    def run(self, project_dir: Path) -> TestRunResult:
        """Invoke pytest in ``project_dir`` and return a parsed TestRunResult.

        Uses the current interpreter (``sys.executable -m pytest``) so
        it picks up whatever venv the CLI is running under. Captures
        stdout+stderr combined, parses the final summary line for
        passed/failed/error counts, and times the subprocess itself.
        Timeout is fixed at 60 seconds.
        """
        start = time.monotonic()
        completed = self._invoke(project_dir)
        elapsed_ms = int((time.monotonic() - start) * 1000)
        output = completed.stdout + completed.stderr
        return self._parse(output, elapsed_ms)

    def _invoke(self, project_dir: Path) -> subprocess.CompletedProcess[str]:
        cmd = [sys.executable, "-m", "pytest", "tests/", "-q", "--no-header",
               "--continue-on-collection-errors"]
        if self._exclude_glob is not None:
            cmd.extend(["--ignore-glob", self._exclude_glob])
        return subprocess.run(
            cmd,
            cwd=str(project_dir),
            capture_output=True,
            text=True,
            timeout=_TIMEOUT_SECONDS,
            check=False,
        )

    def _parse(self, output: str, elapsed_ms: int) -> TestRunResult:
        passed = self._extract(_PASSED, output)
        failed = self._extract(_FAILED, output)
        errors = self._extract(_ERRORS, output)
        return TestRunResult(
            passed=passed,
            failed=failed,
            errors=errors,
            duration_ms=elapsed_ms,
            raw_output=output,
        )

    def _extract(self, pattern: re.Pattern[str], output: str) -> int:
        match = pattern.search(output)
        return int(match.group(1)) if match is not None else 0
