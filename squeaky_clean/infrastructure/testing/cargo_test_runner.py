"""CargoTestRunner: shells out to `cargo test --quiet` and parses summary lines."""

from __future__ import annotations

import re
import subprocess
import time
from pathlib import Path

from squeaky_clean.application.dtos.test_run_result import TestRunResult
from squeaky_clean.infrastructure.observability.json_logger import JSONLogger
from squeaky_clean.infrastructure.testing.test_runner import TestRunner

_TIMEOUT_SECONDS: int = 300
_MAX_OUTPUT: int = 8000
_RESULT_LINE: re.Pattern[str] = re.compile(
    r"test result:\s*\w+\.\s*(\d+)\s+passed;\s*(\d+)\s+failed",
)


class CargoTestRunner(TestRunner):
    """Runs ``cargo test --quiet`` and parses pass/fail counts from result lines."""

    def __init__(self, exclude_glob: str | None = None) -> None:
        self._exclude_glob: str | None = exclude_glob
        self._logger: JSONLogger = JSONLogger()

    def run(self, project_dir: Path) -> TestRunResult:
        """Invoke ``cargo test --quiet`` in ``project_dir`` and return a result.

        Sums ``passed``/``failed`` across every ``test result: ok. N
        passed; M failed`` line so multi-binary crates aggregate
        correctly. Returns a zero-result with a warning on missing
        ``cargo`` or 5-minute timeout.
        """
        start = time.monotonic()
        try:
            completed = self._invoke(project_dir)
        except FileNotFoundError:
            self._logger.event("cargo_not_available", project=str(project_dir))
            return TestRunResult(0, 0, 0, 0, "cargo not available")
        except subprocess.TimeoutExpired:
            self._logger.event("cargo_timeout", project=str(project_dir))
            elapsed = int((time.monotonic() - start) * 1000)
            return TestRunResult(0, 0, 0, elapsed, "cargo timeout")
        elapsed = int((time.monotonic() - start) * 1000)
        combined = completed.stdout + completed.stderr
        passed, failed = _sum_results(combined)
        return TestRunResult(passed, failed, 0, elapsed, combined[:_MAX_OUTPUT])

    def _invoke(self, project_dir: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["cargo", "test", "--quiet"], cwd=str(project_dir),
            capture_output=True, text=True,
            timeout=_TIMEOUT_SECONDS, check=False,
        )


def _sum_results(output: str) -> tuple[int, int]:
    """Sum ``passed``/``failed`` across all ``test result:`` summary lines."""
    passed = failed = 0
    for match in _RESULT_LINE.finditer(output):
        passed += int(match.group(1))
        failed += int(match.group(2))
    return passed, failed
