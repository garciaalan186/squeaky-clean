"""EmitJavaEntitySerialization: give a Java entity a real toJson().

Python serialises an event with `json.dumps`; TypeScript with
`JSON.stringify`. Java has no built-in, so a generated use case calls
`event.toJson()` on an entity that never declares it — "cannot find symbol".
When a `.toJson()` call targets an entity, inject a deterministic `toJson()`
(plus escaping + map helpers) that emits the entity's fields under their
EXACT declared names. Java only.
"""

from __future__ import annotations

import re
from pathlib import Path

from squeaky_clean.application.dtos.language_toolkit import LanguageToolkit
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec


def _snake_to_camel(name: str) -> str:
    parts = name.split("_")
    return parts[0] + "".join(p[:1].upper() + p[1:] for p in parts[1:])

_SERIALIZABLE = frozenset({"Entity", "ValueObject", "Aggregate"})
_MAP = ("map", "dict")
_NUMERIC = ("int", "long", "double", "float", "short", "byte", "boolean")
_HELPERS = (
    "    private static String toJsonStr(String v) {\n"
    "        if (v == null) { return \"null\"; }\n"
    "        return \"\\\"\" + v.replace(\"\\\\\", \"\\\\\\\\\")"
    ".replace(\"\\\"\", \"\\\\\\\"\") + \"\\\"\";\n"
    "    }\n"
    "    private static String toJsonMap(java.util.Map<String, String> m) {\n"
    "        StringBuilder sb = new StringBuilder(\"{\");\n"
    "        boolean first = true;\n"
    "        for (java.util.Map.Entry<String, String> e : m.entrySet()) {\n"
    "            if (!first) { sb.append(\",\"); }\n"
    "            sb.append(toJsonStr(e.getKey())).append(\":\")"
    ".append(toJsonStr(e.getValue()));\n"
    "            first = false;\n"
    "        }\n"
    "        return sb.append(\"}\").toString();\n"
    "    }\n"
)


class EmitJavaEntitySerialization:
    """Injects a deterministic toJson() into entities that need one."""

    def emit(
        self, arch: ArchitectureSpec, output_dir: Path,
        toolkit: LanguageToolkit,
    ) -> int:
        """Inject toJson() into entities called with `.toJson()`; return count."""
        if toolkit.language.value != "java":
            return 0
        fields = self._fields(arch)
        if not fields:
            return 0
        wanted = self._targets(output_dir, set(fields))
        count = 0
        for name in wanted:
            for path in (output_dir / "src").rglob(f"{name}.java"):
                if self._inject(path, name, fields[name]):
                    count += 1
        return count

    def _fields(
        self, arch: ArchitectureSpec,
    ) -> dict[str, list[tuple[str, str, str]]]:
        out: dict[str, list[tuple[str, str, str]]] = {}
        for module in arch.modules:
            for cls in module.classes:
                if cls.pattern not in _SERIALIZABLE or not cls.fields:
                    continue
                out[cls.name] = [self._field(f) for f in cls.fields]
        return out

    def _field(self, entry: str) -> tuple[str, str, str]:
        key = entry.split(":", 1)[0].strip()
        ftype = entry.split(":", 1)[1].strip().lower() if ":" in entry else "str"
        java = _snake_to_camel(key)
        if any(m in ftype for m in _MAP):
            kind = "map"
        elif ftype.startswith(_NUMERIC):
            kind = "raw"
        else:
            kind = "str"
        return key, java, kind

    def _targets(self, output_dir: Path, entities: set[str]) -> set[str]:
        alt = "|".join(re.escape(e) for e in entities)
        wanted: set[str] = set()
        for path in (output_dir / "src").rglob("*.java"):
            text = path.read_text()
            var_type = {m.group(2): m.group(1)
                        for m in re.finditer(rf"\b({alt})\s+(\w+)\b", text)}
            for m in re.finditer(r"\b(\w+)\.toJson\(\)", text):
                owner = var_type.get(m.group(1))
                if owner is not None:
                    wanted.add(owner)
        return wanted

    def _inject(
        self, path: Path, name: str, fields: list[tuple[str, str, str]],
    ) -> bool:
        text = path.read_text()
        if "public String toJson()" in text:
            return False
        close = text.rfind("}")
        if close == -1:
            return False
        body = self._method(fields) + _HELPERS
        path.write_text(text[:close] + body + text[close:])
        return True

    @staticmethod
    def _value(java: str, kind: str) -> str:
        if kind == "map":
            return f"toJsonMap(this.{java})"
        if kind == "raw":
            return f"String.valueOf(this.{java})"
        return f"toJsonStr(this.{java})"

    def _method(self, fields: list[tuple[str, str, str]]) -> str:
        lines = ["    public String toJson() {",
                 "        StringBuilder sb = new StringBuilder(\"{\");"]
        for i, (key, java, kind) in enumerate(fields):
            sep = "" if i == 0 else ","
            lines.append(
                f"        sb.append(\"{sep}\\\"{key}\\\":\")"
                f".append({self._value(java, kind)});")
        lines.append("        return sb.append(\"}\").toString();")
        lines.append("    }")
        return "\n".join(lines) + "\n"
