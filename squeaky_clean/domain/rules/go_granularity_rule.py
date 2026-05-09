"""GoGranularityRule: size/method/arg limits for .go source files."""

import re
from pathlib import Path

from squeaky_clean.application.dtos.violation import Violation
from squeaky_clean.domain.interfaces.rule import Rule

_FUNC_DECL: re.Pattern[str] = re.compile(
    r"^func\s+(?:\(\s*\w+\s+\*?(\w+)\s*\)\s+)?([A-Z]\w*)\s*\(([^)]*)\)",
    re.MULTILINE,
)


class GoGranularityRule(Rule):
    """Parses one Go file and flags granularity violations.

    Detects exported free functions and exported methods on a
    receiver (struct). Enforces <=80 lines/file, <=3 exported
    funcs/methods per receiver (or per-file for free funcs), and
    <=2 args per method (excluding the receiver).
    Skips ``_test.go`` files and anything under ``vendor/``.
    """

    _NAME = "GoGranularityRule"
    _MAX_LINES = 80
    _MAX_METHODS = 3
    _MAX_ARGS = 2

    def check(self, path: Path) -> list[Violation]:
        """Inspect one .go file and return any granularity violations."""
        if path.suffix != ".go" or path.name.endswith("_test.go"):
            return []
        if "vendor" in path.parts:
            return []
        source = path.read_text()
        out: list[Violation] = []
        line_count = len(source.splitlines())
        if line_count > self._MAX_LINES:
            out.append(self._v(path, f"file has {line_count} lines (>80)"))
        out.extend(self._check_funcs(source, path))
        return out

    def _check_funcs(self, source: str, path: Path) -> list[Violation]:
        out: list[Violation] = []
        groups: dict[str, list[tuple[str, str]]] = {}
        for receiver, name, params in _FUNC_DECL.findall(source):
            key = receiver or ""
            groups.setdefault(key, []).append((name, params))
        for receiver, funcs in groups.items():
            label = receiver if receiver else "file"
            if len(funcs) > self._MAX_METHODS:
                out.append(self._v(
                    path, f"{label} has {len(funcs)} exported funcs (>3)",
                ))
            for name, params in funcs:
                count = self._count_args(params)
                if count > self._MAX_ARGS:
                    out.append(self._v(
                        path, f"{name} has {count} args (>2)",
                    ))
        return out

    def _count_args(self, params: str) -> int:
        stripped = params.strip()
        if not stripped:
            return 0
        return stripped.count(",") + 1

    def _v(self, path: Path, message: str) -> Violation:
        return Violation(rule_name=self._NAME, file_path=str(path), message=message)
