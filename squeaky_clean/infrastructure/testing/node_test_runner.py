"""NodeTestRunner: shells out to `node --test tests/` and parses the summary."""

import fnmatch
import re
import subprocess
import time
from pathlib import Path

from squeaky_clean.application.dtos.test_run_result import TestRunResult
from squeaky_clean.infrastructure.testing.test_runner import TestRunner

_TIMEOUT_SECONDS: int = 60
_PASS: re.Pattern[str] = re.compile(r"^#\s*pass\s+(\d+)", re.MULTILINE)
_FAIL: re.Pattern[str] = re.compile(r"^#\s*fail\s+(\d+)", re.MULTILINE)


class NodeTestRunner(TestRunner):
    """Runs ``node --test tests/`` against a project dir and parses the summary."""

    def __init__(self, exclude_glob: str | None = None) -> None:
        self._exclude_glob: str | None = exclude_glob

    def run(self, project_dir: Path) -> TestRunResult:
        """Invoke node --test in ``project_dir`` and return a parsed TestRunResult.

        Uses the system ``node`` binary from PATH, captures
        stdout+stderr combined, parses the ``# pass`` / ``# fail``
        summary lines that node's TAP reporter emits, and times the
        subprocess itself. Timeout is fixed at 60 seconds.
        """
        start = time.monotonic()
        completed = self._invoke(project_dir)
        elapsed_ms = int((time.monotonic() - start) * 1000)
        output = completed.stdout + completed.stderr
        return self._parse(output, elapsed_ms)

    def _invoke(self, project_dir: Path) -> subprocess.CompletedProcess[str]:
        cmd = ["node", "--test"]
        if self._exclude_glob is not None:
            files = self._filtered_files(project_dir)
            cmd.extend(files if files else ["tests/"])
        else:
            cmd.append("tests/")
        return subprocess.run(
            cmd,
            cwd=str(project_dir),
            capture_output=True,
            text=True,
            timeout=_TIMEOUT_SECONDS,
            check=False,
        )

    def _filtered_files(self, project_dir: Path) -> list[str]:
        tests_dir = project_dir / "tests"
        if not tests_dir.is_dir():
            return []
        files: list[str] = []
        for f in sorted(tests_dir.iterdir()):
            if f.is_file() and not fnmatch.fnmatch(f.name, self._exclude_glob or ""):
                files.append(str(f.relative_to(project_dir)))
        return files

    def _parse(self, output: str, elapsed_ms: int) -> TestRunResult:
        passed = self._extract(_PASS, output)
        failed = self._extract(_FAIL, output)
        return TestRunResult(
            passed=passed,
            failed=failed,
            errors=0,
            duration_ms=elapsed_ms,
            raw_output=output,
        )

    def _extract(self, pattern: re.Pattern[str], output: str) -> int:
        match = pattern.search(output)
        return int(match.group(1)) if match is not None else 0
