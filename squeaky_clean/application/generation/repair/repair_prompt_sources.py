"""RepairPromptSources: project text gathered into the test-repair prompt."""

from __future__ import annotations

from pathlib import Path

from squeaky_clean.application.shared.language.language_toolkit import LanguageToolkit


class RepairPromptSources:
    """Reads the generated project for prompt context (source + style)."""

    def exemplar(self, project_dir: Path, exclude_rel: str) -> str:
        """An existing test file to copy the framework/import style from."""
        for p in sorted(project_dir.rglob("*")):
            name = p.name
            is_test = (name.startswith("test_") and name.endswith(".py")) \
                or name.endswith((".test.ts", ".test.js")) \
                or name.endswith("Test.java")
            if not is_test or "node_modules" in p.parts or "target" in p.parts:
                continue
            if str(p.relative_to(project_dir)) == exclude_rel:
                continue
            try:
                return p.read_text()[:2000]
            except OSError:
                continue
        return ""

    def sources(self, project_dir: Path, toolkit: LanguageToolkit) -> str:
        """Concatenate the production source files (excluding tests)."""
        ext = toolkit.file_extension
        out: list[str] = []
        for p in sorted(project_dir.rglob(f"*{ext}")):
            parts = p.parts
            if "test" in parts or "tests" in parts or p.name.endswith(f".test{ext}"):
                continue
            if "node_modules" in parts or "dist" in parts or "target" in parts:
                continue
            try:
                out.append(f"// {p.name}\n{p.read_text()}")
            except OSError:
                continue
        return "\n\n".join(out)[:12000]
