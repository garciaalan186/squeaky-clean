"""WiringLanguageEmitters: non-Python composition-root emission dispatch."""

from __future__ import annotations

from pathlib import Path

from squeaky_clean.application.generation.integration.wiring_templates import (
    render_express_main,
    render_fastify_main,
    render_go_main,
    render_rust_main,
    render_spring_boot_main,
)
from squeaky_clean.domain.interfaces.project_file_system import ProjectFileSystem
from squeaky_clean.domain.value_objects.tech_spec import TechSpec


class WiringLanguageEmitters:
    """Emits the composition root for Java/Go/Rust/TS/JS targets.

    Returns None when no held TechSpec declares one of those languages,
    letting WiringGenerator fall back to the Python ``src/main.py`` path.
    """

    def __init__(self, fs: ProjectFileSystem) -> None:
        self._fs: ProjectFileSystem = fs

    def emit(self, tech_specs: dict[str, TechSpec], output_dir: Path) -> Path | None:
        """Write the first matching non-Python root; None = Python fallback."""
        if self._has(tech_specs, "java"):
            path = output_dir / "src" / "main" / "java" / "com" / "example" / "App.java"
            self._fs.write(path, render_spring_boot_main())
            return path
        if self._has(tech_specs, "go"):
            path = output_dir / "main.go"
            self._fs.write(path, render_go_main(self._cats(tech_specs, "go")))
            return path
        if self._has(tech_specs, "rust"):
            path = output_dir / "src" / "main.rs"
            self._fs.write(path, render_rust_main(self._cats(tech_specs, "rust")))
            return path
        if self._has(tech_specs, "typescript"):
            path = output_dir / "src" / "index.ts"
            # Carry the technology (not a bare True) so the renderer can match
            # the wiring's HTTP framework to the resolved handler (e.g. express).
            cats: dict[str, object] = {s.category: s.technology
                                       for s in tech_specs.values()
                                       if s.language == "typescript"}
            self._fs.write(path, render_fastify_main(cats))
            return path
        if self._has(tech_specs, "javascript"):
            path = output_dir / "index.js"
            self._fs.write(
                path, render_express_main(self._cats(tech_specs, "javascript")),
            )
            return path
        return None

    @staticmethod
    def _has(tech_specs: dict[str, TechSpec], language: str) -> bool:
        return any(s.language == language for s in tech_specs.values())

    @staticmethod
    def _cats(tech_specs: dict[str, TechSpec], language: str) -> dict[str, object]:
        return {s.category: True for s in tech_specs.values()
                if s.language == language}
