"""JavaGranularityRule: enforces size/class/method/arg limits for .java files."""

import re
from pathlib import Path

from squeaky_clean.application.dtos.violation import Violation
from squeaky_clean.domain.interfaces.rule import Rule

_CLASS_DECL: re.Pattern[str] = re.compile(
    r"^\s*(?:public\s+)?(?:final\s+)?class\s+(\w+)", re.MULTILINE
)
_METHOD_SIG: re.Pattern[str] = re.compile(
    r"^\s*public\s+(?:static\s+)?[\w<>\[\]]+\s+(\w+)\s*\(([^)]*)\)",
    re.MULTILINE,
)


class JavaGranularityRule(Rule):
    """Parses one Java file and flags granularity violations."""

    _NAME = "JavaGranularityRule"
    _MAX_LINES = 80
    _MAX_METHODS = 3
    _MAX_ARGS = 2

    def check(self, path: Path) -> list[Violation]:
        """Inspect one .java file and return any granularity violations."""
        if path.suffix != ".java":
            return []
        source = path.read_text()
        out: list[Violation] = []
        line_count = len(source.splitlines())
        if line_count > self._MAX_LINES:
            out.append(self._v(path, f"file has {line_count} lines (>80)"))
        class_names = _CLASS_DECL.findall(source)
        if len(class_names) > 1:
            out.append(
                self._v(path, f"file declares {len(class_names)} classes (>1)")
            )
        if class_names:
            out.extend(self._check_methods(source, class_names[0], path))
        return out

    def _check_methods(
        self, source: str, class_name: str, path: Path
    ) -> list[Violation]:
        out: list[Violation] = []
        methods = [
            (name, params)
            for name, params in _METHOD_SIG.findall(source)
            if name != class_name
        ]
        if len(methods) > self._MAX_METHODS:
            out.append(
                self._v(
                    path,
                    f"class {class_name} has {len(methods)} public methods (>3)",
                )
            )
        for name, params in methods:
            count = self._count_args(params)
            if count > self._MAX_ARGS:
                out.append(
                    self._v(path, f"method {name} has {count} args (>2)")
                )
        return out

    def _count_args(self, params: str) -> int:
        stripped = params.strip()
        if not stripped:
            return 0
        depth = 0
        count = 1
        for ch in stripped:
            if ch in "(<[":
                depth += 1
            elif ch in ")>]":
                depth -= 1
            elif ch == "," and depth == 0:
                count += 1
        return count

    def _v(self, path: Path, message: str) -> Violation:
        return Violation(
            rule_name=self._NAME, file_path=str(path), message=message
        )
