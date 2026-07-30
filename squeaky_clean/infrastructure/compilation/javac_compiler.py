"""JavacCompiler: compile a bare .java file set with the JDK's javac (R5.4)."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

from squeaky_clean.domain.interfaces.project_compiler import ProjectCompiler
from squeaky_clean.domain.value_objects.compile_result import CompileResult

_TIMEOUT_SECONDS: int = 60
# javac emits ``<path>.java:<line>: error: <msg>``.
_ERROR_LINE: re.Pattern[str] = re.compile(r"([\w./\\-]+\.java):\d+: error:")


class JavacCompiler(ProjectCompiler):
    """Compiles every .java under a dir with raw ``javac`` (no Maven/pom).

    Micro-eval cells (R5.4) are a handful of sibling classes with no
    third-party dependencies; invoking the JDK directly avoids requiring a
    generated pom.xml and is an order of magnitude faster than ``mvn``.
    """

    def compile(self, project_dir: Path) -> CompileResult:
        """Compile all .java files under ``project_dir`` together."""
        files = sorted(
            str(p) for p in project_dir.rglob("*.java")
            if "_out" not in p.parts
        )
        if not files:
            return CompileResult(
                ok=False, error_count=1, offending_stems=(),
                raw_output="no .java files found",
            )
        out_dir = project_dir / "_out"
        out_dir.mkdir(exist_ok=True)
        completed = subprocess.run(
            ["javac", "-d", str(out_dir), *files],
            cwd=str(project_dir), capture_output=True, text=True,
            timeout=_TIMEOUT_SECONDS, check=False,
        )
        return self._parse(completed.stdout + completed.stderr)

    @staticmethod
    def _parse(output: str) -> CompileResult:
        paths = _ERROR_LINE.findall(output)
        stems = tuple(sorted({Path(p).stem for p in paths}))
        return CompileResult(
            ok=len(paths) == 0, error_count=len(paths),
            offending_stems=stems, raw_output=output,
        )
