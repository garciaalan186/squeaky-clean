"""tsconfig_generator: emit tsconfig.json for TypeScript projects."""

from __future__ import annotations

import json
from pathlib import Path

from squeaky_clean.application.generation.integration.manifests.manifest_write_error import (
    ManifestWriteError,
)
from squeaky_clean.application.shared.problem.problem_spec import ProblemSpec
from squeaky_clean.domain.interfaces.project_file_system import ProjectFileSystem
from squeaky_clean.domain.value_objects.tech_spec import TechSpec


def _has_typescript(tech_specs: dict[str, TechSpec]) -> bool:
    return any(s.language == "typescript" for s in tech_specs.values())


def generate(
    tech_specs: dict[str, TechSpec],
    output_dir: Path,
    problem: ProblemSpec,
    *, fs: ProjectFileSystem,
) -> Path | None:
    """Emit ``<output_dir>/tsconfig.json`` for TypeScript runs.

    Emits when ``problem.target_language`` is TypeScript or any TechSpec
    declares ``language == 'typescript'``. None means ONLY "not a
    TypeScript run"; write failures raise ``ManifestWriteError`` (R6.8).
    """
    is_ts = (str(getattr(problem.target_language, "value", "")).lower()
             == "typescript") or _has_typescript(tech_specs)
    if not is_ts:
        return None
    body = {
        "compilerOptions": {
            "target": "ES2022",
            "module": "commonjs",
            "strict": True,
            "esModuleInterop": True,
            "skipLibCheck": True,
            "forceConsistentCasingInFileNames": True,
            "outDir": "./dist",
            "rootDir": "./src",
            "resolveJsonModule": True,
        },
        "include": ["src/**/*"],
        "exclude": ["node_modules", "dist"],
    }
    path = output_dir / "tsconfig.json"
    try:
        fs.write(path, json.dumps(body, indent=2) + "\n")
    except OSError as exc:
        raise ManifestWriteError(f"tsconfig.json write failed: {exc}") from exc
    return path
