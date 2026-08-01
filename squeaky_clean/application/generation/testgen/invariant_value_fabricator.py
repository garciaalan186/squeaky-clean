"""InvariantValueFabricator: constructor args that violate one invariant."""

from __future__ import annotations

import re

_STR = ("str", "string")
_DICT = ("dict", "map")


class InvariantValueFabricator:
    """Builds a constructor arg list where ONE value breaks the invariant."""

    def __init__(self, lang: str) -> None:
        """``lang`` is the toolkit language value (python/typescript/.../java)."""
        self._lang = lang

    def args(self, fields: list[tuple[str, str]], inv: str) -> str:
        """Comma-joined values: defaults except the constrained field."""
        target = self._constrained(inv, fields)
        vals = [self._violate(inv, t) if n == target
                else self._default(t) for n, t in fields]
        return ", ".join(vals)

    @staticmethod
    def _constrained(inv: str, fields: list[tuple[str, str]]) -> str:
        low = inv.lower()
        for name, _ in fields:
            if re.search(rf"\b{re.escape(name.lower())}\b", low):
                return name
        return fields[0][0] if fields else ""

    def _default(self, ftype: str) -> str:
        low = ftype.lower()
        lang = self._lang
        if any(d in low for d in _DICT):
            return "new java.util.HashMap<String, String>()" if lang == "java" else "{}"
        if "[]" in low or "list" in low:
            return "new String[]{}" if lang == "java" else "[]"
        if low.startswith(("int", "float", "double", "long", "number")):
            return "0"
        if low.startswith("bool"):
            return "false" if lang != "python" else "False"
        return '"x"' if lang != "typescript" else "'x'"

    def _violate(self, inv: str, ftype: str) -> str:
        low = inv.lower()
        lang = self._lang
        if any(s in ftype.lower() for s in _STR):
            if any(k in low for k in ("empty", "blank")):
                return "''" if lang == "typescript" else '""'
            if any(k in low for k in ("length", "byte", "char")):
                n = self._limit(low)
                if n is not None:
                    return self._repeat(n + 1)
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

    def _repeat(self, n: int) -> str:
        if self._lang == "python":
            return f'"x" * {n}'
        if self._lang == "java":
            return f'"x".repeat({n})'
        return f"'x'.repeat({n})"
