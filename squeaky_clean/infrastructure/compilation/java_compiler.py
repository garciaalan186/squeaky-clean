"""JavaCompiler: compile a generated Maven project with ``mvn test-compile``."""

import os
import re
import subprocess
from pathlib import Path

from squeaky_clean.application.dtos.compile_result import CompileResult
from squeaky_clean.domain.interfaces.project_compiler import ProjectCompiler
from squeaky_clean.infrastructure.testing.maven_test_runner import _resolve_java_home

_TIMEOUT_SECONDS: int = 300
# Strip ANSI colour escapes mvn emits even under capture, so the marker parses.
_ANSI: re.Pattern[str] = re.compile(r"\x1b\[[0-9;]*m")
# mvn emits ``[ERROR] <path>.java:[line,col] <msg>`` for compile failures.
_ERROR_LINE: re.Pattern[str] = re.compile(
    r"^\[ERROR\]\s+(?P<path>\S+\.java):\[\d+,\d+\]", re.MULTILINE)


class JavaCompiler(ProjectCompiler):
    """Runs ``mvn -q test-compile`` and parses errors + offending src stems."""

    def compile(self, project_dir: Path) -> CompileResult:
        """Compile ``project_dir``; report errors + implicated src stems."""
        try:
            completed = self._invoke(project_dir)
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return CompileResult(True, 0, (), "maven unavailable")
        output = completed.stdout + completed.stderr
        return self._parse(output)

    def _invoke(self, project_dir: Path) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        java_home = _resolve_java_home()
        if java_home is not None:
            env["JAVA_HOME"] = java_home
        return subprocess.run(
            # -B (batch mode) disables ANSI colour so `[ERROR]` markers parse.
            ["mvn", "-B", "-q", "test-compile"], cwd=str(project_dir),
            capture_output=True, text=True, timeout=_TIMEOUT_SECONDS,
            check=False, env=env,
        )

    def _parse(self, output: str) -> CompileResult:
        output = _ANSI.sub("", output)
        paths = _ERROR_LINE.findall(output)
        stems = self._src_stems(paths)
        return CompileResult(
            ok=len(paths) == 0, error_count=len(paths),
            offending_stems=stems, raw_output=output[:8000],
        )

    @staticmethod
    def _src_stems(paths: list[str]) -> tuple[str, ...]:
        """Unique class stems from production ``src/main`` errors only."""
        out: list[str] = []
        for raw in paths:
            p = Path(raw)
            if "test" in p.parts:
                continue
            stem = p.name[: -len(".java")]
            if stem not in out:
                out.append(stem)
        return tuple(out)
