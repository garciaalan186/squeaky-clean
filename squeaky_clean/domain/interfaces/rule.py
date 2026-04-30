"""Rule port: abstract interface for a single architectural rule check."""

from abc import ABC, abstractmethod
from pathlib import Path

from squeaky_clean.application.dtos.violation import Violation


class Rule(ABC):
    """Port for a rule that inspects either a single file or a project dir.

    Implementations return a list of Violation records (empty list
    means the input was clean). RuleRunner walks project files and
    dispatches per-file rules; whole-project rules are invoked once
    with the project root.
    """

    @abstractmethod
    def check(self, path: Path) -> list[Violation]:
        """Inspect ``path`` and return any violations found."""
