"""InvariantTestRenderer: render a deterministic invariants test file."""

from __future__ import annotations

from squeaky_clean.application.generation.testgen.invariant_value_fabricator import (
    InvariantValueFabricator,
)
from squeaky_clean.application.shared.language.language_toolkit import LanguageToolkit
from squeaky_clean.application.shared.language.pascal_to_camel_converter import (
    PascalToCamelConverter,
)
from squeaky_clean.application.shared.language.snake_case_converter import SnakeCaseConverter
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec


class InvariantTestRenderer:
    """Renders (relative_path, file_body) of a class's invariants test."""

    def __init__(self, toolkit: LanguageToolkit, module: ModuleSpec) -> None:
        """Constructed per module: ``module`` owns the classes it renders."""
        self._toolkit = toolkit
        self._module = module
        self._snake = SnakeCaseConverter()
        self._camel = PascalToCamelConverter()

    def render(
        self, cls: ClassSpec, invariants: tuple[str, ...],
    ) -> tuple[str, str]:
        fields = [(e.split(":", 1)[0].strip(),
                   e.split(":", 1)[1].strip() if ":" in e else "str")
                  for e in cls.fields]
        lang = self._toolkit.language.value
        if lang == "python":
            return self._python(cls, self._module, fields, invariants)
        if lang in ("typescript", "javascript"):
            return self._ts(cls, fields, invariants, lang)
        return self._java(cls, fields, invariants)

    def _python(
        self, cls: ClassSpec, module: ModuleSpec,
        fields: list[tuple[str, str]], invs: tuple[str, ...],
    ) -> tuple[str, str]:
        fab = InvariantValueFabricator("python")
        stem = self._snake.convert(cls.name)
        dotted = (f"src.{module.layer.value.lower()}."
                  f"{self._snake.convert(module.name)}.{stem}")
        lines = ["import pytest", f"from {dotted} import {cls.name}", ""]
        for i, inv in enumerate(invs):
            lines += [
                f"def test_{stem}_invariant_{i}() -> None:",
                f'    # invariant: {inv}',
                "    with pytest.raises(Exception):",
                f"        {cls.name}({fab.args(fields, inv)})", ""]
        return f"tests/test_{stem}_invariants.py", "\n".join(lines)

    def _ts(
        self, cls: ClassSpec, fields: list[tuple[str, str]],
        invs: tuple[str, ...], lang: str,
    ) -> tuple[str, str]:
        fab = InvariantValueFabricator(lang)
        stem = self._camel.convert(cls.name)
        ext = "ts" if lang == "typescript" else "js"
        lines = ["import { test } from 'node:test';",
                 "import assert from 'node:assert/strict';",
                 f"import {{ {cls.name} }} from '../src/{stem}.js';", ""]
        for i, inv in enumerate(invs):
            lines += [
                f"test('{cls.name} invariant {i}: {inv[:40]}', () => {{",
                f"  assert.throws(() => new {cls.name}"
                f"({fab.args(fields, inv)}));",
                "});", ""]
        return f"tests/{stem}Invariants.test.{ext}", "\n".join(lines)

    def _java(
        self, cls: ClassSpec, fields: list[tuple[str, str]],
        invs: tuple[str, ...],
    ) -> tuple[str, str]:
        fab = InvariantValueFabricator("java")
        lines = ["package com.example;",
                 "import org.junit.jupiter.api.Test;",
                 "import static org.junit.jupiter.api.Assertions.*;", "",
                 f"class {cls.name}InvariantsTest {{"]
        for i, inv in enumerate(invs):
            lines += [
                f"    @Test void invariant{i}() {{",
                f"        assertThrows(RuntimeException.class, () -> new "
                f"{cls.name}({fab.args(fields, inv)}));", "    }"]
        lines.append("}")
        path = f"src/test/java/com/example/{cls.name}InvariantsTest.java"
        return path, "\n".join(lines)
