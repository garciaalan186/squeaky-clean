"""PythonSyntaxCompiler: ast-parse every .py as a cheap compile gate (R5.4)."""

from __future__ import annotations

import ast
from pathlib import Path

from squeaky_clean.domain.interfaces.project_compiler import ProjectCompiler
from squeaky_clean.domain.value_objects.compile_result import CompileResult


class PythonSyntaxCompiler(ProjectCompiler):
    """Syntax-checks every .py under a dir via ``ast.parse``.

    Python has no ahead-of-time compile step, so the micro-eval (R5.4)
    compile gate reduces to "is this parseable Python" — which still
    catches truncated emissions, stray prose, and malformed defs.
    """

    def compile(self, project_dir: Path) -> CompileResult:
        """Parse all .py files under ``project_dir``; report syntax errors."""
        errors: list[str] = []
        stems: list[str] = []
        for path in sorted(project_dir.rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            try:
                ast.parse(path.read_text())
            except SyntaxError as exc:
                errors.append(f"{path.name}:{exc.lineno}: {exc.msg}")
                stems.append(path.stem)
        return CompileResult(
            ok=not errors, error_count=len(errors),
            offending_stems=tuple(sorted(set(stems))),
            raw_output="\n".join(errors),
        )
