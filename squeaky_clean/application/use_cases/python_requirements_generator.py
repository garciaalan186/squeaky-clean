"""python_requirements_generator: emit requirements.txt from Python TechSpecs."""

from __future__ import annotations

from pathlib import Path

from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.application.dtos.tech_spec import TechSpec
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec


def _is_pip_spec(spec: TechSpec) -> bool:
    if spec.language != "python":
        return False
    manager = str(spec.install.get("manager", ""))
    return manager == "pip"


def _emit_line(raw: str) -> str | None:
    """Normalize ``install.package`` (e.g. ``confluent-kafka==2.5``).

    Returns the trimmed package spec or None for empty / stdlib values.
    """
    line = raw.strip()
    if not line or line == "stdlib":
        return None
    return line


def generate(
    architecture: ArchitectureSpec,
    tech_specs: dict[str, TechSpec],
    output_dir: Path,
    problem: ProblemSpec,
) -> Path | None:
    """Emit ``<output_dir>/requirements.txt`` from Python ``pip`` TechSpecs.

    Skips ``manager == "stdlib"`` entries (already on the interpreter
    path). Returns the written path, or None if no Python TechSpecs
    declare a pip dependency. Best-effort on OSError.
    """
    del architecture  # currently unused; kept for interface symmetry
    del problem
    pip_specs = [s for s in tech_specs.values() if _is_pip_spec(s)]
    if not pip_specs:
        return None
    seen: set[str] = set()
    lines: list[str] = []
    for s in pip_specs:
        line = _emit_line(str(s.install.get("package", "")))
        if line is None or line in seen:
            continue
        seen.add(line)
        lines.append(line)
    if not lines:
        return None
    path = output_dir / "requirements.txt"
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(lines) + "\n")
    except OSError:
        return None
    return path
