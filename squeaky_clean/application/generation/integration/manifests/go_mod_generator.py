"""go_mod_generator: emit a go.mod manifest from resolved Go TechSpecs."""

from __future__ import annotations

from pathlib import Path

from squeaky_clean.application.shared.problem.problem_spec import ProblemSpec
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.interfaces.project_file_system import ProjectFileSystem
from squeaky_clean.domain.value_objects.tech_spec import TechSpec


def _parse_go_package(raw: str) -> tuple[str, str] | None:
    """Parse `<module-path>@<version>` into ``(path, version)``.

    Returns None when the raw value cannot be split (e.g. ``stdlib``).
    """
    if "@" not in raw:
        return None
    path, _, version = raw.partition("@")
    path = path.strip()
    version = version.strip()
    if not path or not version:
        return None
    return path, version


def generate_go_mod(
    architecture: ArchitectureSpec,
    tech_specs: dict[str, TechSpec],
    output_dir: Path,
    problem: ProblemSpec,
    *, fs: ProjectFileSystem,
) -> Path | None:
    """Emit ``<output_dir>/go.mod`` and return the path.

    None means ONLY "not applicable" (no Go TechSpecs). Write errors are
    never swallowed here: ``fs.write`` OSErrors propagate to the
    ManifestEmitter, which logs them as a failure event (R6.8).
    """
    del architecture  # currently unused; kept for interface symmetry
    go_specs = [s for s in tech_specs.values() if s.language == "go"]
    if not go_specs:
        return None
    requires: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for s in go_specs:
        parsed = _parse_go_package(str(s.install.get("package", "")))
        if parsed is None or parsed in seen:
            continue
        seen.add(parsed)
        requires.append(parsed)
    body = _render_body(problem.slug, requires)
    path = output_dir / "go.mod"
    fs.write(path, body)
    return path


def _render_body(slug: str, requires: list[tuple[str, str]]) -> str:
    head = f"module com.example/{slug}\n\ngo 1.21\n"
    if not requires:
        return head
    lines = "\n".join(f"\t{p} {v}" for p, v in requires)
    return f"{head}\nrequire (\n{lines}\n)\n"
