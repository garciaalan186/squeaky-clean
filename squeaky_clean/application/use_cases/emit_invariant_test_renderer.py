"""InvariantTestRenderer: render a deterministic invariants test file."""

from __future__ import annotations

import re

from squeaky_clean.application.dtos.language_toolkit import LanguageToolkit
from squeaky_clean.application.use_cases.pascal_to_camel_converter import (
    PascalToCamelConverter,
)
from squeaky_clean.application.use_cases.snake_case_converter import SnakeCaseConverter
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec

_STR = ("str", "string")
_DICT = ("dict", "map")


class InvariantTestRenderer:
    """Renders (relative_path, file_body) of a class's invariants test."""

    def __init__(self, toolkit: LanguageToolkit) -> None:
        self._toolkit = toolkit
        self._snake = SnakeCaseConverter()
        self._camel = PascalToCamelConverter()

    def render(
        self, cls: ClassSpec, module: ModuleSpec, invariants: tuple[str, ...],
    ) -> tuple[str, str]:
        fields = [(e.split(":", 1)[0].strip(),
                   e.split(":", 1)[1].strip() if ":" in e else "str")
                  for e in cls.fields]
        lang = self._toolkit.language.value
        if lang == "python":
            return self._python(cls, module, fields, invariants)
        if lang in ("typescript", "javascript"):
            return self._ts(cls, fields, invariants, lang)
        return self._java(cls, fields, invariants)

    def _args(self, fields: list[tuple[str, str]], inv: str, lang: str) -> str:
        target = self._constrained(inv, fields)
        vals = [self._violate(inv, t, lang) if n == target
                else self._default(t, lang) for n, t in fields]
        return ", ".join(vals)

    @staticmethod
    def _constrained(inv: str, fields: list[tuple[str, str]]) -> str:
        low = inv.lower()
        for name, _ in fields:
            if re.search(rf"\b{re.escape(name.lower())}\b", low):
                return name
        return fields[0][0] if fields else ""

    @staticmethod
    def _default(ftype: str, lang: str) -> str:
        low = ftype.lower()
        if any(d in low for d in _DICT):
            return "new java.util.HashMap<String, String>()" if lang == "java" else "{}"
        if "[]" in low or "list" in low:
            return "new String[]{}" if lang == "java" else "[]"
        if low.startswith(("int", "float", "double", "long", "number")):
            return "0"
        if low.startswith("bool"):
            return "false" if lang != "python" else "False"
        return '"x"' if lang != "typescript" else "'x'"

    def _violate(self, inv: str, ftype: str, lang: str) -> str:
        low = inv.lower()
        if any(s in ftype.lower() for s in _STR):
            if any(k in low for k in ("empty", "blank")):
                return "''" if lang == "typescript" else '""'
            if any(k in low for k in ("length", "byte", "char")):
                n = self._limit(low)
                if n is not None:
                    return self._repeat(n + 1, lang)
            return "'!'" if lang == "typescript" else '"!"'  # invalid format
        # numeric bound: overshoot an upper bound, else go negative
        if any(k in low for k in ("<=", "at most", "less than", "up to",
                                  "below", "no more")):
            n = self._limit(low)
            return str(n + 1 if n is not None else 999999999)
        return "-1"

    @staticmethod
    def _limit(inv: str) -> int | None:
        m = re.search(r"(\d[\d,]*)", inv)
        return int(m.group(1).replace(",", "")) if m is not None else None

    @staticmethod
    def _repeat(n: int, lang: str) -> str:
        if lang == "python":
            return f'"x" * {n}'
        if lang == "java":
            return f'"x".repeat({n})'
        return f"'x'.repeat({n})"

    def _python(
        self, cls: ClassSpec, module: ModuleSpec,
        fields: list[tuple[str, str]], invs: tuple[str, ...],
    ) -> tuple[str, str]:
        stem = self._snake.convert(cls.name)
        dotted = (f"src.{module.layer.value.lower()}."
                  f"{self._snake.convert(module.name)}.{stem}")
        lines = ["import pytest", f"from {dotted} import {cls.name}", ""]
        for i, inv in enumerate(invs):
            lines += [
                f"def test_{stem}_invariant_{i}() -> None:",
                f'    # invariant: {inv}',
                "    with pytest.raises(Exception):",
                f"        {cls.name}({self._args(fields, inv, 'python')})", ""]
        return f"tests/test_{stem}_invariants.py", "\n".join(lines)

    def _ts(
        self, cls: ClassSpec, fields: list[tuple[str, str]],
        invs: tuple[str, ...], lang: str,
    ) -> tuple[str, str]:
        stem = self._camel.convert(cls.name)
        ext = "ts" if lang == "typescript" else "js"
        lines = ["import { test } from 'node:test';",
                 "import assert from 'node:assert/strict';",
                 f"import {{ {cls.name} }} from '../src/{stem}.js';", ""]
        for i, inv in enumerate(invs):
            lines += [
                f"test('{cls.name} invariant {i}: {inv[:40]}', () => {{",
                f"  assert.throws(() => new {cls.name}"
                f"({self._args(fields, inv, lang)}));",
                "});", ""]
        return f"tests/{stem}Invariants.test.{ext}", "\n".join(lines)

    def _java(
        self, cls: ClassSpec, fields: list[tuple[str, str]],
        invs: tuple[str, ...],
    ) -> tuple[str, str]:
        lines = ["package com.example;",
                 "import org.junit.jupiter.api.Test;",
                 "import static org.junit.jupiter.api.Assertions.*;", "",
                 f"class {cls.name}InvariantsTest {{"]
        for i, inv in enumerate(invs):
            lines += [
                f"    @Test void invariant{i}() {{",
                f"        assertThrows(RuntimeException.class, () -> new "
                f"{cls.name}({self._args(fields, inv, 'java')}));", "    }"]
        lines.append("}")
        path = f"src/test/java/com/example/{cls.name}InvariantsTest.java"
        return path, "\n".join(lines)
