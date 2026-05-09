"""GoTestRunner: shells out to `go test -json ./...` and parses JSON events."""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

from squeaky_clean.application.dtos.test_run_result import TestRunResult
from squeaky_clean.infrastructure.observability.json_logger import JSONLogger
from squeaky_clean.infrastructure.testing.test_runner import TestRunner

_TIMEOUT_SECONDS: int = 300
_MAX_OUTPUT: int = 8000


class GoTestRunner(TestRunner):
    """Runs ``go test -v -count=1 -json ./...`` and parses pass/fail events."""

    def __init__(self, exclude_glob: str | None = None) -> None:
        self._exclude_glob: str | None = exclude_glob
        self._logger: JSONLogger = JSONLogger()

    def run(self, project_dir: Path) -> TestRunResult:
        """Invoke ``go test`` in ``project_dir`` and return a parsed result.

        Streams ``go test``'s line-delimited JSON output and counts
        ``Action: pass`` / ``Action: fail`` events on real test names.
        Returns a zero-result with a warning on missing toolchain or
        timeout (5-minute cap).
        """
        start = time.monotonic()
        try:
            completed = self._invoke(project_dir)
        except FileNotFoundError:
            self._logger.event("go_not_available", project=str(project_dir))
            return TestRunResult(0, 0, 0, 0, "go not available")
        except subprocess.TimeoutExpired:
            self._logger.event("go_timeout", project=str(project_dir))
            elapsed = int((time.monotonic() - start) * 1000)
            return TestRunResult(0, 0, 0, elapsed, "go timeout")
        elapsed = int((time.monotonic() - start) * 1000)
        output = (completed.stdout + completed.stderr)[:_MAX_OUTPUT]
        passed, failed = _count_events(completed.stdout)
        return TestRunResult(passed, failed, 0, elapsed, output)

    def _invoke(self, project_dir: Path) -> subprocess.CompletedProcess[str]:
        cmd = ["go", "test", "-v", "-count=1", "-json", "./..."]
        return subprocess.run(
            cmd, cwd=str(project_dir), capture_output=True, text=True,
            timeout=_TIMEOUT_SECONDS, check=False,
        )


def _count_events(stdout: str) -> tuple[int, int]:
    """Return ``(passed, failed)`` from go test's line-delimited JSON output."""
    passed = failed = 0
    for line in stdout.splitlines():
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not event.get("Test"):
            continue
        action = event.get("Action")
        if action == "pass":
            passed += 1
        elif action == "fail":
            failed += 1
    return passed, failed
