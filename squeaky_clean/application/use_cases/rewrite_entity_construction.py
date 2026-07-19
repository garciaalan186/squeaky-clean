"""RewriteEntityConstruction: deterministically fix entity construction.

TypeScript's structural typing lets the model return a plain object literal
`{ id, received_at, ... }` where a domain class is required — it type-checks
until the class has a method (an Entity's `equals`), then fails. Prompting
the model away from this proved unreliable, so rewrite it deterministically:
a `return { ... }` whose keys exactly match a domain class's fields becomes
`return new <Class>(<values in field order>)`.
"""

from __future__ import annotations

from pathlib import Path

from squeaky_clean.application.dtos.language_toolkit import LanguageToolkit
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec

_OPEN = "([{<"
_CLOSE = ")]}>"
_CONSTRUCTABLE = frozenset({"Entity", "ValueObject", "Aggregate"})


class RewriteEntityConstruction:
    """Rewrites object-literal entity construction into constructor calls."""

    def rewrite(
        self, arch: ArchitectureSpec, output_dir: Path,
        toolkit: LanguageToolkit,
    ) -> int:
        """Rewrite object-literal returns in TS/JS src; return rewrite count."""
        lang = toolkit.language.value
        if lang not in ("typescript", "javascript"):
            return 0
        ext = ".ts" if lang == "typescript" else ".js"
        fields = self._entity_fields(arch)
        if not fields:
            return 0
        total = 0
        src = output_dir / "src"
        for path in sorted(src.rglob(f"*{ext}")):
            if path.name.endswith((".test.ts", ".test.js")):
                continue
            text = path.read_text()
            new_text, n = self._rewrite_file(text, fields)
            if n:
                path.write_text(new_text)
                total += n
        return total

    @staticmethod
    def _entity_fields(arch: ArchitectureSpec) -> dict[str, list[str]]:
        out: dict[str, list[str]] = {}
        for module in arch.modules:
            for cls in module.classes:
                if cls.pattern not in _CONSTRUCTABLE or not cls.fields:
                    continue
                names = [f.split(":", 1)[0].strip() for f in cls.fields]
                out[cls.name] = names
        return out

    def _rewrite_file(
        self, text: str, fields: dict[str, list[str]],
    ) -> tuple[str, int]:
        out: list[str] = []
        i = 0
        count = 0
        marker = "return {"
        while True:
            idx = text.find(marker, i)
            if idx == -1:
                out.append(text[i:])
                break
            brace = idx + len("return ")
            end = self._match_brace(text, brace)
            ctor = (self._to_ctor(text[brace + 1:end], fields)
                    if end != -1 else None)
            if ctor is not None:
                out.append(text[i:idx])
                out.append(f"return {ctor}")
                i = end + 1
                count += 1
            else:
                stop = end + 1 if end != -1 else idx + len(marker)
                out.append(text[i:stop])
                i = stop
        return "".join(out), count

    def _to_ctor(
        self, body: str, fields: dict[str, list[str]],
    ) -> str | None:
        pairs = self._pairs(body)
        if not pairs:
            return None
        keys = {k for k, _ in pairs}
        value_of = dict(pairs)
        for name, order in fields.items():
            if keys == set(order):
                return f"new {name}({', '.join(value_of[f] for f in order)})"
        return None

    def _pairs(self, body: str) -> list[tuple[str, str]]:
        pairs: list[tuple[str, str]] = []
        for item in self._split(body, ","):
            item = item.strip()
            if not item:
                continue
            colon = self._top_index(item, ":")
            if colon == -1:
                pairs.append((item, item))
            else:
                pairs.append((item[:colon].strip(), item[colon + 1:].strip()))
        return pairs

    @staticmethod
    def _match_brace(text: str, pos: int) -> int:
        depth = 0
        for i in range(pos, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    return i
        return -1

    def _split(self, s: str, sep: str) -> list[str]:
        parts: list[str] = []
        depth = 0
        last = 0
        for i, ch in enumerate(s):
            if ch in _OPEN:
                depth += 1
            elif ch in _CLOSE:
                depth = max(0, depth - 1)
            elif ch == sep and depth == 0:
                parts.append(s[last:i])
                last = i + 1
        parts.append(s[last:])
        return parts

    @staticmethod
    def _top_index(s: str, target: str) -> int:
        depth = 0
        for i, ch in enumerate(s):
            if ch in _OPEN:
                depth += 1
            elif ch in _CLOSE:
                depth = max(0, depth - 1)
            elif ch == target and depth == 0:
                return i
        return -1
