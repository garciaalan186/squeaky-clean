"""micro_eval_scaffold: static per-language config for micro-evals (R5.4)."""

from __future__ import annotations

from squeaky_clean.domain.interfaces.project_compiler import ProjectCompiler
from squeaky_clean.domain.value_objects.target_language import TargetLanguage
from squeaky_clean.infrastructure.compilation.cargo_check_compiler import (
    CargoCheckCompiler,
)
from squeaky_clean.infrastructure.compilation.go_build_compiler import GoBuildCompiler
from squeaky_clean.infrastructure.compilation.javac_compiler import JavacCompiler
from squeaky_clean.infrastructure.compilation.node_syntax_compiler import (
    NodeSyntaxCompiler,
)
from squeaky_clean.infrastructure.compilation.python_syntax_compiler import (
    PythonSyntaxCompiler,
)
from squeaky_clean.infrastructure.compilation.typescript_compiler import (
    TypeScriptCompiler,
)

# R6.1d: the matrix grows toward 6 columns. This tuple is the single
# source of truth — micro_eval_implementers derives from it too.
LANGUAGES: tuple[TargetLanguage, ...] = (
    TargetLanguage.PYTHON, TargetLanguage.JAVA, TargetLanguage.TYPESCRIPT,
    TargetLanguage.JAVASCRIPT, TargetLanguage.GO, TargetLanguage.RUST,
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
    # ESM resolution for `node --check`, mirroring the full-run bootstrap.
    TargetLanguage.JAVASCRIPT.value: {
        "package.json": '{"type": "module"}',
    },
    # R6.1d: flat single-package Go cell — go.mod pins the lowest toolchain
    # the emitters promise (JDK-neutral analog); the zz_main shim satisfies
    # `go build` for a `package main` holding only types.
    TargetLanguage.GO.value: {
        "go.mod": "module microeval\n\ngo 1.18\n",
        "src/zz_main.go": "package main\n\nfunc main() {}\n",
    },
    # R6.1d: cargo cell manifest; src/lib.rs is synthesized per-cell by
    # CargoCheckCompiler from the emitted module files.
    TargetLanguage.RUST.value: {
        "Cargo.toml": (
            '[package]\nname = "microeval"\nversion = "0.1.0"\n'
            'edition = "2021"\n'
        ),
    },
}


def compilers() -> dict[str, ProjectCompiler]:
    """Per-language compile-gate adapters for micro-eval cells."""
    return {
        TargetLanguage.PYTHON.value: PythonSyntaxCompiler(),
        TargetLanguage.JAVA.value: JavacCompiler(),
        TargetLanguage.TYPESCRIPT.value: TypeScriptCompiler(),
        TargetLanguage.JAVASCRIPT.value: NodeSyntaxCompiler(),
        TargetLanguage.GO.value: GoBuildCompiler(),
        TargetLanguage.RUST.value: CargoCheckCompiler(),
    }
