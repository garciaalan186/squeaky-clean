"""JavaScriptGranularityRule: enforces size/class/method/arg limits for .js files."""

import re
from pathlib import Path

from squeaky_clean.application.dtos.violation import Violation
from squeaky_clean.domain.interfaces.rule import Rule
from squeaky_clean.domain.rules.javascript_method_scanner import JavaScriptMethodScanner

_CLASS_DECL: re.Pattern[str] = re.compile(
    r"^\s*(?:export\s+(?:default\s+)?)?class\s+(\w+)", re.MULTILINE
)


class JavaScriptGranularityRule(Rule):
    """Parses one JavaScript file and flags granularity violations."""

    _NAME = "JavaScriptGranularityRule"
    _MAX_LINES = 80

    def __init__(self) -> None:
        self._scanner: JavaScriptMethodScanner = JavaScriptMethodScanner()

    def check(self, path: Path) -> list[Violation]:
        """Inspect one .js file and return any granularity violations."""
        if path.suffix != ".js":
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
            for message in self._scanner.scan(source, class_names[0]):
                out.append(self._v(path, message))
        return out

    def _v(self, path: Path, message: str) -> Violation:
        return Violation(rule_name=self._NAME, file_path=str(path), message=message)
