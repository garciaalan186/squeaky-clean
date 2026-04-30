"""TypeScriptTestRunner: compiles TS with tsc then runs node --test on dist/."""

import fnmatch
import re
import subprocess
import time
from pathlib import Path

from squeaky_clean.application.dtos.test_run_result import TestRunResult
from squeaky_clean.infrastructure.testing.test_runner import TestRunner

_TIMEOUT_SECONDS: int = 120
_PASS: re.Pattern[str] = re.compile(r"^#\s*pass\s+(\d+)", re.MULTILINE)
_FAIL: re.Pattern[str] = re.compile(r"^#\s*fail\s+(\d+)", re.MULTILINE)


class TypeScriptTestRunner(TestRunner):
    """Compiles TypeScript with ``npx tsc``, then runs ``node --test dist/tests/``."""

    def __init__(self, exclude_glob: str | None = None) -> None:
        self._exclude_glob: str | None = exclude_glob

    def run(self, project_dir: Path) -> TestRunResult:
        """Install deps, compile TS, run tests, and return a parsed TestRunResult."""
        start = time.monotonic()
        install = self._exec(["npm", "install"], project_dir)
        if install.returncode != 0:
            return self._error(install, start)
        compile_step = self._exec(["npx", "tsc"], project_dir)
        if compile_step.returncode != 0:
            return self._error(compile_step, start)
        test_cmd = ["node", "--test"]
        if self._exclude_glob is not None:
            files = self._filtered_files(project_dir)
            test_cmd.extend(files if files else ["dist/tests/"])
        else:
            test_cmd.append("dist/tests/")
        test_step = self._exec(test_cmd, project_dir)
        elapsed_ms = int((time.monotonic() - start) * 1000)
        output = test_step.stdout + test_step.stderr
        return self._parse(output, elapsed_ms)

    def _exec(
        self, cmd: list[str], cwd: Path
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            cmd,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=_TIMEOUT_SECONDS,
            check=False,
        )

    def _error(
        self,
        result: subprocess.CompletedProcess[str],
        start: float,
    ) -> TestRunResult:
        elapsed_ms = int((time.monotonic() - start) * 1000)
        output = result.stdout + result.stderr
        return TestRunResult(
            passed=0,
            failed=0,
            errors=1,
            duration_ms=elapsed_ms,
            raw_output=output,
        )

    def _filtered_files(self, project_dir: Path) -> list[str]:
        tests_dir = project_dir / "dist" / "tests"
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
