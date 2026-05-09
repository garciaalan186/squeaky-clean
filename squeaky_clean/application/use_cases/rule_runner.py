"""RuleRunner: apply a tuple of Rule implementations to a project directory."""

from pathlib import Path

from squeaky_clean.application.dtos.violation import Violation
from squeaky_clean.domain.interfaces.rule import Rule


class RuleRunner:
    """Walks source files under a project root and runs every Rule on each."""

    def __init__(self, rules: tuple[Rule, ...], file_extension: str = ".py") -> None:
        self._rules: tuple[Rule, ...] = rules
        self._glob: str = f"*{file_extension}"

    def run(self, project_dir: Path) -> tuple[Violation, ...]:
        """Return every Violation produced by any rule on any source file.

        Walks ``project_dir`` recursively, invokes ``rule.check(path)``
        on each source file matching the configured extension per rule,
        and concatenates the results. If ``project_dir`` does not exist,
        returns an empty tuple.
        """
        if not project_dir.exists():
            return ()
        out: list[Violation] = []
        files = sorted(p for p in project_dir.rglob(self._glob) if p.is_file())
        for path in files:
            for rule in self._rules:
                out.extend(rule.check(path))
        return tuple(out)
