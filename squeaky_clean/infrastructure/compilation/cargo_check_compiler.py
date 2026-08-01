"""CargoCheckCompiler: ``cargo check`` as the micro-eval compile gate (R6.1d)."""

from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

from squeaky_clean.domain.interfaces.project_compiler import ProjectCompiler
from squeaky_clean.domain.value_objects.compile_result import CompileResult

_TIMEOUT_SECONDS: int = 180
# rustc emits ``error[E0308]: ...`` / ``error: ...`` headers.
_ERROR_LINE: re.Pattern[str] = re.compile(r"^error(\[E\d+\])?:", re.MULTILINE)
_FILE_LINE: re.Pattern[str] = re.compile(
    r"^\s+--> (?P<path>[^\s:]+\.rs):\d+:\d+", re.MULTILINE,
)


class CargoCheckCompiler(ProjectCompiler):
    """Runs ``cargo check`` in the cell dir and parses rustc errors.

    The cell scaffold supplies ``Cargo.toml``; this adapter synthesizes
    ``src/lib.rs`` (one ``pub mod <stem>;`` per emitted module, per the
    rust language profile's file-is-a-module convention) before checking.
    A missing cargo toolchain raises — never a silent green.
    """

    def compile(self, project_dir: Path) -> CompileResult:
        """Check ``project_dir``; report error count + offending stems."""
        if shutil.which("cargo") is None:
            raise RuntimeError("cargo toolchain not installed (R6.1d gate)")
        self._write_lib_rs(project_dir / "src")
        completed = subprocess.run(
            ["cargo", "check", "--quiet"], cwd=str(project_dir),
            capture_output=True, text=True,
            timeout=_TIMEOUT_SECONDS, check=False,
        )
        output = completed.stdout + completed.stderr
        errors = _ERROR_LINE.findall(output)
        stems = {
            Path(p).stem for p in _FILE_LINE.findall(output)
            if Path(p).stem != "lib"
        }
        ok = completed.returncode == 0
        return CompileResult(
            ok=ok, error_count=len(errors) if errors else (0 if ok else 1),
            offending_stems=tuple(sorted(stems)),
            raw_output=output,
        )

    @staticmethod
    def _write_lib_rs(src_dir: Path) -> None:
        """Declare every emitted .rs as a public module of the check crate."""
        src_dir.mkdir(parents=True, exist_ok=True)
        stems = sorted(
            p.stem for p in src_dir.glob("*.rs") if p.stem != "lib"
        )
        body = "".join(f"pub mod {stem};\n" for stem in stems)
        (src_dir / "lib.rs").write_text(body)
