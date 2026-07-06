"""TypeScriptCompiler: typecheck a generated TS project with ``npx tsc``."""

import re
import subprocess
from pathlib import Path

from squeaky_clean.application.dtos.compile_result import CompileResult
from squeaky_clean.domain.interfaces.project_compiler import ProjectCompiler

_TIMEOUT_SECONDS: int = 120
# tsc emits ``<path>(line,col): error TS<code>: <msg>``.
_ERROR_LINE: re.Pattern[str] = re.compile(
    r"^(?P<path>[^\s(]+\.ts)\(\d+,\d+\):\s+error\s+TS\d+", re.MULTILINE)


class TypeScriptCompiler(ProjectCompiler):
    """Runs ``npx tsc --noEmit`` and parses errors + offending src stems."""

    def compile(self, project_dir: Path) -> CompileResult:
        """Typecheck ``project_dir``; report errors + implicated src stems."""
        if not (project_dir / "node_modules").is_dir():
            self._exec(["npm", "install"], project_dir)
        completed = self._exec(["npx", "tsc", "--noEmit"], project_dir)
        output = completed.stdout + completed.stderr
        return self._parse(output)

    def _exec(
        self, cmd: list[str], cwd: Path,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            cmd, cwd=str(cwd), capture_output=True, text=True,
            timeout=_TIMEOUT_SECONDS, check=False,
        )

    def _parse(self, output: str) -> CompileResult:
        paths = _ERROR_LINE.findall(output)
        stems = self._src_stems(paths)
        return CompileResult(
            ok=len(paths) == 0, error_count=len(paths),
            offending_stems=stems, raw_output=output,
        )

    @staticmethod
    def _src_stems(paths: list[str]) -> tuple[str, ...]:
        """Unique class-file stems from production ``src/`` errors only.

        Test-file errors (``*.test.ts``, ``tests/``) are excluded: they
        indicate test/impl drift, not a production-code compile bug.
        """
        out: list[str] = []
        for raw in paths:
            p = Path(raw)
            if "tests" in p.parts or p.name.endswith(".test.ts"):
                continue
            if "src" not in p.parts:
                continue
            stem = p.name[: -len(".ts")]
            if stem not in out:
                out.append(stem)
        return tuple(out)
