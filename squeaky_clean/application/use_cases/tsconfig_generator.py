"""tsconfig_generator: emit tsconfig.json for TypeScript projects."""

from __future__ import annotations

import json
from pathlib import Path

from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.application.dtos.tech_spec import TechSpec


def _has_typescript(tech_specs: dict[str, TechSpec]) -> bool:
    return any(s.language == "typescript" for s in tech_specs.values())


def generate(
    tech_specs: dict[str, TechSpec],
    output_dir: Path,
    problem: ProblemSpec,
) -> Path | None:
    """Emit ``<output_dir>/tsconfig.json`` for TypeScript runs.

    Always emits when ``problem.target_language`` is TypeScript or any
    TechSpec declares ``language == 'typescript'``. Best-effort on
    OSError. Returns the written path or ``None`` on failure / when
    not applicable.
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
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(body, indent=2) + "\n")
    except OSError:
        return None
    return path
