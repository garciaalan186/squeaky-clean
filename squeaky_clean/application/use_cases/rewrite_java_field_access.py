"""RewriteJavaFieldAccess: read a value object's field through its getter.

Java entities/value objects expose `private final` fields with public
getters, but generated adapters/use-cases sometimes read the field directly
(`key.value`), which does not compile across the class boundary. This
rewrites `<var>.<field>` to `<var>.get<Field>()` when `<var>` is declared
(as a parameter or local) with a domain value-object / entity type — a
deterministic, type-directed fix.
"""

from __future__ import annotations

import re
from pathlib import Path

from squeaky_clean.application.dtos.language_toolkit import LanguageToolkit
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec


def _snake_to_camel(name: str) -> str:
    parts = name.split("_")
    return parts[0] + "".join(p[:1].upper() + p[1:] for p in parts[1:])

_CONSTRUCTABLE = frozenset({"Entity", "ValueObject", "Aggregate"})


class RewriteJavaFieldAccess:
    """Rewrites direct field reads on VO/Entity variables into getter calls."""

    def rewrite(
        self, arch: ArchitectureSpec, output_dir: Path,
        toolkit: LanguageToolkit,
    ) -> int:
        """Rewrite `<var>.<field>` -> getter in Java src; return count."""
        if toolkit.language.value != "java":
            return 0
        getters = self._getters(arch)
        if not getters:
            return 0
        total = 0
        for path in sorted((output_dir / "src").rglob("*.java")):
            if path.name.endswith("Test.java"):
                continue
            text = path.read_text()
            new_text, n = self._rewrite_file(text, getters)
            if n:
                path.write_text(new_text)
                total += n
        return total

    def _getters(
        self, arch: ArchitectureSpec,
    ) -> dict[str, dict[str, str]]:
        out: dict[str, dict[str, str]] = {}
        for module in arch.modules:
            for cls in module.classes:
                if cls.pattern not in _CONSTRUCTABLE or not cls.fields:
                    continue
                field_map: dict[str, str] = {}
                for entry in cls.fields:
                    field = _snake_to_camel(entry.split(":", 1)[0].strip())
                    field_map[field] = f"get{field[:1].upper()}{field[1:]}"
                out[cls.name] = field_map
        return out

    def _rewrite_file(
        self, text: str, getters: dict[str, dict[str, str]],
    ) -> tuple[str, int]:
        var_type = self._var_types(text, set(getters))
        count = 0

        def repl(m: re.Match[str]) -> str:
            nonlocal count
            var, field = m.group(1), m.group(2)
            fields = getters.get(var_type.get(var, ""), {})
            if field in fields:
                count += 1
                return f"{var}.{fields[field]}()"
            return m.group(0)

        # <var>.<field> not already a call (no following "(")
        new_text = re.sub(r"\b(\w+)\.(\w+)\b(?!\s*\()", repl, text)
        return new_text, count

    @staticmethod
    def _var_types(text: str, types: set[str]) -> dict[str, str]:
        """Map local/parameter variable names to their VO/Entity type."""
        alt = "|".join(re.escape(t) for t in types)
        out: dict[str, str] = {}
        for m in re.finditer(rf"\b({alt})\s+(\w+)\b", text):
            out[m.group(2)] = m.group(1)
        return out
