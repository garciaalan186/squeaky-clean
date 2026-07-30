"""micro_eval_scaffold: static per-language config for micro-evals (R5.4)."""

from __future__ import annotations

from squeaky_clean.domain.interfaces.project_compiler import ProjectCompiler
from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.infrastructure.compilation.javac_compiler import JavacCompiler
from squeaky_clean.infrastructure.compilation.python_syntax_compiler import (
    PythonSyntaxCompiler,
)
from squeaky_clean.infrastructure.compilation.typescript_compiler import (
    TypeScriptCompiler,
)

LANGUAGES: tuple[TargetLanguage, ...] = (
    TargetLanguage.PYTHON, TargetLanguage.JAVA, TargetLanguage.TYPESCRIPT,
)

# Mirrors the tsconfig the integration bootstrap generates for full runs.
_TSCONFIG = (
    '{"compilerOptions": {"target": "ES2022", "module": "nodenext",'
    ' "moduleResolution": "nodenext", "strict": true, "noEmit": true,'
    ' "esModuleInterop": true, "skipLibCheck": true},'
    ' "include": ["src/**/*.ts"]}'
)

EXTRA_FILES: dict[str, dict[str, str]] = {
    TargetLanguage.TYPESCRIPT.value: {
        "tsconfig.json": _TSCONFIG,
        "package.json": '{"type": "module"}',
    },
}


def compilers() -> dict[str, ProjectCompiler]:
    """Per-language compile-gate adapters for micro-eval cells."""
    return {
        TargetLanguage.PYTHON.value: PythonSyntaxCompiler(),
        TargetLanguage.JAVA.value: JavacCompiler(),
        TargetLanguage.TYPESCRIPT.value: TypeScriptCompiler(),
    }
