"""cargo_toml_generator: emit a Cargo.toml manifest from resolved Rust TechSpecs."""

from __future__ import annotations

from pathlib import Path

from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.application.dtos.tech_spec import TechSpec
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec

_TOKIO_LINE = 'tokio = { version = "1.36", features = ["full"] }'


def _parse_rust_package(raw: str) -> tuple[str, str] | None:
    """Parse ``<crate>==<version>`` into ``(crate, version)``.

    Returns None for stdlib/empty markers.
    """
    if "==" not in raw:
        return None
    crate, _, version = raw.partition("==")
    crate = crate.strip()
    version = version.strip()
    if not crate or not version:
        return None
    return crate, version


def generate_cargo_toml(
    architecture: ArchitectureSpec,
    tech_specs: dict[str, TechSpec],
    output_dir: Path,
    problem: ProblemSpec,
) -> Path | None:
    """Emit ``<output_dir>/Cargo.toml`` and return the path (or None when no Rust)."""
    del architecture  # currently unused; kept for interface symmetry
    rust_specs = [s for s in tech_specs.values() if s.language == "rust"]
    if not rust_specs:
        return None
    deps: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for s in rust_specs:
        parsed = _parse_rust_package(str(s.install.get("package", "")))
        if parsed is None or parsed in seen:
            continue
        seen.add(parsed)
        deps.append(parsed)
    body = _render_body(problem.slug, deps)
    path = output_dir / "Cargo.toml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body)
    return path


def _render_body(slug: str, deps: list[tuple[str, str]]) -> str:
    head = (f'[package]\nname = "{slug}"\nversion = "0.1.0"\n'
            'edition = "2021"\n\n[dependencies]\n')
    lines = [_TOKIO_LINE]
    for crate, version in deps:
        lines.append(f'{crate} = "{version}"')
    return head + "\n".join(lines) + "\n"
