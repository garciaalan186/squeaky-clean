"""NodeSyntaxCompiler: ``node --check`` every .js as a cheap compile gate."""

from __future__ import annotations

import subprocess
from pathlib import Path

from squeaky_clean.domain.interfaces.project_compiler import ProjectCompiler
from squeaky_clean.domain.value_objects.compile_result import CompileResult

_TIMEOUT_SECONDS: int = 60


class NodeSyntaxCompiler(ProjectCompiler):
    """Syntax-checks every .js under a dir via ``node --check`` (R6.1d).

    JavaScript has no ahead-of-time compile step, so the micro-eval gate
    reduces to Node's parser — which still catches truncated emissions,
    stray prose, and malformed syntax. Module type (ESM) is resolved from
    the cell's scaffolded ``package.json`` (``{"type": "module"}``), same
    as the full-run integration bootstrap.
    """

    def compile(self, project_dir: Path) -> CompileResult:
        """Parse-check all .js files under ``project_dir``."""
        errors: list[str] = []
        stems: list[str] = []
        for path in sorted(project_dir.rglob("*.js")):
            if "node_modules" in path.parts:
                continue
            completed = subprocess.run(
                ["node", "--check", str(path)], cwd=str(project_dir),
                capture_output=True, text=True,
                timeout=_TIMEOUT_SECONDS, check=False,
            )
            if completed.returncode != 0:
                errors.append(f"{path.name}: {completed.stderr.strip()}")
                stems.append(path.stem)
        return CompileResult(
            ok=not errors, error_count=len(errors),
            offending_stems=tuple(sorted(set(stems))),
            raw_output="\n".join(errors),
        )
