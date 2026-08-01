"""package_json_generator: emit package.json from JS/TS TechSpecs."""

from __future__ import annotations

import json
from pathlib import Path

from squeaky_clean.application.generation.integration.manifests.manifest_write_error import (
    ManifestWriteError,
)
from squeaky_clean.application.shared.problem.problem_spec import ProblemSpec
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.interfaces.project_file_system import ProjectFileSystem
from squeaky_clean.domain.value_objects.tech_spec import TechSpec


def _is_npm_spec(spec: TechSpec) -> bool:
    return (spec.language in ("javascript", "typescript")
            and str(spec.install.get("manager", "")) in ("npm", "yarn", "pnpm"))


def _parse_pkg(raw: str) -> tuple[str, str] | None:
    """Parse ``<name>@<version>`` or ``<name>==<version>`` to ``(name, ver)``."""
    line = raw.strip()
    if not line or line == "stdlib":
        return None
    if "==" in line:
        name, _, ver = line.partition("==")
        return name.strip(), ver.strip()
    # npm form: ``<name>@<ver>`` / scoped ``@scope/name@<ver>`` — the version
    # delimiter is the LAST ``@`` and never the leading scope char (index 0).
    at = line.rfind("@")
    if at > 0:
        return line[:at].strip(), line[at + 1:].strip()
    return line, "*"


def generate(
    architecture: ArchitectureSpec,
    tech_specs: dict[str, TechSpec],
    output_dir: Path,
    problem: ProblemSpec,
    *, fs: ProjectFileSystem,
) -> Path:
    """Emit ``<output_dir>/package.json`` from JS/TS TechSpecs.

    Always emits for JS/TS runs — an empty ``dependencies`` object when no
    JS/TS TechSpecs exist (NpmDependencyInstaller needs something to run).
    Write failures raise ``ManifestWriteError`` (R6.8) — never a silent None.
    """
    del architecture
    npm_specs = [s for s in tech_specs.values() if _is_npm_spec(s)]
    deps: dict[str, str] = {}
    type_deps: dict[str, str] = {}
    for s in npm_specs:
        parsed = _parse_pkg(str(s.install.get("package", "")))
        if parsed is not None:
            deps[parsed[0]] = parsed[1]
        # A package without bundled typings declares its DefinitelyTyped
        # companion via `types_package` (e.g. express -> @types/express);
        # packages that bundle types (kafkajs) simply omit it.
        typed = _parse_pkg(str(s.install.get("types_package", "")))
        if typed is not None:
            type_deps[typed[0]] = typed[1]
    dev_deps: dict[str, str] = {"jest": "^29.7.0"}
    ts = problem.target_language.value == "typescript"  # R5.9: pin TS always
    if ts or any(s.language == "typescript" for s in npm_specs):
        dev_deps["typescript"] = "^5.4.0"
        dev_deps["ts-jest"] = "^29.1.0"
        dev_deps["@types/node"] = "^20.0.0"
        dev_deps.update(type_deps)
    body = {"name": problem.slug, "version": "1.0.0",
            "dependencies": deps, "devDependencies": dev_deps}
    path = output_dir / "package.json"
    try:
        fs.write(path, json.dumps(body, indent=2) + "\n")
    except OSError as exc:
        raise ManifestWriteError(f"package.json write failed: {exc}") from exc
    return path
