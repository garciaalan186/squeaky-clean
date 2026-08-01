"""JavaToJsonRenderer: the injected toJson() method + escaping/map helpers."""

from __future__ import annotations

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


class JavaToJsonRenderer:
    """Renders the deterministic Java toJson() body for an entity's fields.

    Each field is a ``(json_key, java_name, kind)`` triple where kind is
    ``map`` / ``raw`` / ``str`` — the JSON key keeps the EXACT declared
    name while the Java accessor uses the camelCase field.
    """

    def render(self, fields: list[tuple[str, str, str]]) -> str:
        """The full injected block: toJson() plus its static helpers."""
        return self._method(fields) + _HELPERS

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
