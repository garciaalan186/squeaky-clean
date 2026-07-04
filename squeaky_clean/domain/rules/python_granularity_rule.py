"""PythonGranularityRule: enforces per-file size/class/method/arg limits."""

import ast
from pathlib import Path

from squeaky_clean.application.dtos.violation import Violation
from squeaky_clean.domain.interfaces.rule import Rule


class PythonGranularityRule(Rule):
    """Parses one Python file and flags granularity violations.

    Enforces Hard Rules 1-3 and 8: 1 class/file, <=5 public methods,
    <=2 args per method (excluding self), and <=80 lines per file.
    Non-Python files are skipped (return empty list).
    """

    _NAME = "PythonGranularityRule"
    _MAX_LINES = 80
    _MAX_METHODS = 5
    _MAX_ARGS = 2

    def check(self, path: Path) -> list[Violation]:
        """Inspect one .py file and return any granularity violations."""
        if path.suffix != ".py":
            return []
        source = path.read_text()
        out: list[Violation] = []
        line_count = len(source.splitlines())
        if line_count > self._MAX_LINES:
            out.append(self._v(path, f"file has {line_count} lines (>80)"))
        try:
            tree = ast.parse(source)
        except SyntaxError as exc:
            out.append(self._v(path, f"syntax error: {exc.msg}"))
            return out
        out.extend(self._check_tree(tree, path))
        return out

    def _check_tree(self, tree: ast.Module, path: Path) -> list[Violation]:
        classes = [n for n in tree.body if isinstance(n, ast.ClassDef)]
        out: list[Violation] = []
        if len(classes) > 1:
            out.append(self._v(path, f"file declares {len(classes)} classes (>1)"))
        for cls in classes:
            out.extend(self._check_class(cls, path))
        return out

    def _check_class(self, cls: ast.ClassDef, path: Path) -> list[Violation]:
        out: list[Violation] = []
        methods = [
            m for m in cls.body if isinstance(m, ast.FunctionDef) and not m.name.startswith("_")
        ]
        if len(methods) > self._MAX_METHODS:
            out.append(
                self._v(path, f"{cls.name} has {len(methods)} public methods (>5)")
            )
        for method in methods:
            arg_count = len(method.args.args) - 1
            if arg_count > self._MAX_ARGS:
                out.append(
                    self._v(
                        path,
                        f"{cls.name}.{method.name} has {arg_count} args (>2)",
                    )
                )
        return out

    def _v(self, path: Path, message: str) -> Violation:
        return Violation(rule_name=self._NAME, file_path=str(path), message=message)
