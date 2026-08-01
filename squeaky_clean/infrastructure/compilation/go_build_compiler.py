"""GoBuildCompiler: ``go vet ./...`` as the micro-eval compile gate (R6.1d)."""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

from squeaky_clean.domain.interfaces.project_compiler import ProjectCompiler
from squeaky_clean.domain.value_objects.compile_result import CompileResult

_TIMEOUT_SECONDS: int = 120
# gc/vet emit ``src/point.go:12:34: message`` (vet prefixes with ``vet:``).
_ERROR_LINE: re.Pattern[str] = re.compile(
    r"^(?:vet: )?(?P<path>[^\s:]+\.go):\d+:\d+:", re.MULTILINE,
)


class GoBuildCompiler(ProjectCompiler):
    """Runs ``go vet ./...`` in the cell dir and parses compile errors.

    ``go vet`` type-checks the package without producing a binary (a
    plain ``go build`` would try to write an executable named after the
    package dir and collide with ``src/``).

    The cell scaffold supplies ``go.mod`` and a ``func main`` shim (the
    emitted classes share one flat ``package main`` per the go language
    profile). A missing go toolchain raises — never a silent green.
    """

    def compile(self, project_dir: Path) -> CompileResult:
        """Build ``project_dir``; report error count + offending stems."""
        if shutil.which("go") is None:
            raise RuntimeError("go toolchain not installed (R6.1d gate)")
        completed = subprocess.run(
            ["go", "vet", "./..."], cwd=str(project_dir),
            capture_output=True, text=True,
            timeout=_TIMEOUT_SECONDS, check=False,
        )
        output = completed.stdout + completed.stderr
        paths = _ERROR_LINE.findall(output)
        ok = completed.returncode == 0
        return CompileResult(
            ok=ok, error_count=len(paths) if paths else (0 if ok else 1),
            offending_stems=tuple(sorted({Path(p).stem for p in paths})),
            raw_output=output,
        )
