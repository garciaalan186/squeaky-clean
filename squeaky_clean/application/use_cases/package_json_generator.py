"""package_json_generator: emit package.json from JS/TS TechSpecs."""

from __future__ import annotations

import json
from pathlib import Path

from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.application.dtos.tech_spec import TechSpec
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec


def _is_npm_spec(spec: TechSpec) -> bool:
    if spec.language not in ("javascript", "typescript"):
        return False
    manager = str(spec.install.get("manager", ""))
    return manager in ("npm", "yarn", "pnpm")


def _parse_pkg(raw: str) -> tuple[str, str] | None:
    """Parse ``<name>@<version>`` or ``<name>==<version>`` to ``(name, ver)``."""
    line = raw.strip()
    if not line or line == "stdlib":
        return None
    if "==" in line:
        name, _, ver = line.partition("==")
        return name.strip(), ver.strip()
    if "@" in line and not line.startswith("@"):
        name, _, ver = line.rpartition("@")
        return name.strip(), ver.strip()
    return line, "*"


def generate(
    architecture: ArchitectureSpec,
    tech_specs: dict[str, TechSpec],
    output_dir: Path,
    problem: ProblemSpec,
) -> Path | None:
    """Emit ``<output_dir>/package.json`` from JS/TS TechSpecs.

    Always emits when ``problem.target_language`` is JS/TS — produces
    an empty ``dependencies`` object if no JS/TS TechSpecs exist (so
    NpmDependencyInstaller has something to operate on). Best-effort
    on OSError.
    """
    del architecture
    npm_specs = [s for s in tech_specs.values() if _is_npm_spec(s)]
    deps: dict[str, str] = {}
    for s in npm_specs:
        parsed = _parse_pkg(str(s.install.get("package", "")))
        if parsed is None:
            continue
        deps[parsed[0]] = parsed[1]
    dev_deps: dict[str, str] = {"jest": "^29.7.0"}
    if any(s.language == "typescript" for s in npm_specs):
        dev_deps["typescript"] = "^5.4.0"
        dev_deps["ts-jest"] = "^29.1.0"
        dev_deps["@types/node"] = "^20.0.0"
    body = {"name": problem.slug, "version": "1.0.0",
            "dependencies": deps, "devDependencies": dev_deps}
    path = output_dir / "package.json"
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(body, indent=2) + "\n")
    except OSError:
        return None
    return path
