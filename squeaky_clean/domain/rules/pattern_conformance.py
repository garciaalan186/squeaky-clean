"""PatternConformanceRule: structural checks that a class honours its pattern."""

import ast
from pathlib import Path

from squeaky_clean.domain.interfaces.rule import Rule
from squeaky_clean.domain.value_objects.violation import Violation


class PatternConformanceRule(Rule):
    """Flags a generated class whose structure contradicts its GoF pattern.

    Conservative by design — it only reports HIGH-confidence breakage so it
    never inflates a run's violation count on a merely-unusual-but-valid class:

    * Visitor double dispatch: a method named ``accept`` must delegate to a
      ``visit*`` call on its argument; a stubbed ``accept`` (bare ``pass`` /
      ``...`` or no call at all) is a broken Visitor.

    Other patterns are checked cross-file by ValidateArchitecture and are out
    of scope for this per-file rule.
    """

    _NAME = "PatternConformanceRule"

    def check(self, path: Path) -> list[Violation]:
        """Inspect one .py file for high-confidence pattern breakage."""
        if path.suffix != ".py":
            return []
        try:
            tree = ast.parse(path.read_text())
        except (SyntaxError, OSError):
            return []
        out: list[Violation] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "accept":
                if not self._delegates_to_visitor(node):
                    out.append(self._v(
                        path,
                        f"accept() in {node.name!r} does not delegate to a "
                        "visit* call (broken Visitor double dispatch)",
                    ))
        return out

    @staticmethod
    def _delegates_to_visitor(fn: ast.FunctionDef) -> bool:
        """True if the body calls a ``visit*`` method on some object."""
        for call in ast.walk(fn):
            if (
                isinstance(call, ast.Call)
                and isinstance(call.func, ast.Attribute)
                and call.func.attr.startswith("visit")
            ):
                return True
        return False

    def _v(self, path: Path, message: str) -> Violation:
        return Violation(
            rule_name=self._NAME, file_path=str(path), message=message,
        )
