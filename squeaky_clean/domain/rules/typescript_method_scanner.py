"""TypeScriptMethodScanner: parses method signatures out of a TS class body."""

import re

_METHOD_SIG: re.Pattern[str] = re.compile(
    r"^\s*(?:async\s+|static\s+)*(\w+)\s*\(([^)]*)\)(?:\s*:\s*\S+)?\s*\{",
    re.MULTILINE,
)
_KEYWORDS: frozenset[str] = frozenset(
    {"if", "for", "while", "switch", "return", "catch", "do"}
)
_MAX_METHODS: int = 5
_MAX_ARGS: int = 2


class TypeScriptMethodScanner:
    """Scans a TS class body and reports method-count / arg-count violations."""

    def scan(self, source: str, class_name: str) -> list[str]:
        """Return violation messages for a TS class."""
        body = self._body(source)
        if body is None:
            return []
        methods = [
            (name, args)
            for name, args in _METHOD_SIG.findall(body)
            if name != "constructor"
            and not name.startswith("_")
            and name not in _KEYWORDS
        ]
        out: list[str] = []
        if len(methods) > _MAX_METHODS:
            out.append(
                f"class {class_name} has {len(methods)} public methods (>5)"
            )
        for name, args in methods:
            count = self._count(args)
            if count > _MAX_ARGS:
                out.append(f"method {name} has {count} args (>2)")
        return out

    def _body(self, source: str) -> str | None:
        match = re.search(r"class\s+\w+[^{]*\{", source)
        if match is None:
            return None
        start = match.end()
        depth = 1
        for i in range(start, len(source)):
            ch = source[i]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return source[start:i]
        return None

    def _count(self, params: str) -> int:
        stripped = params.strip()
        if not stripped:
            return 0
        depth = 0
        count = 1
        for ch in stripped:
            if ch in "([{":
                depth += 1
            elif ch in ")]}":
                depth -= 1
            elif ch == "," and depth == 0:
                count += 1
        return count
