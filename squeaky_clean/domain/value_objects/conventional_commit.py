"""ConventionalCommit value object: structured commit message."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ConventionalCommit:
    """A Conventional Commits-formatted message with type, scope, and description."""

    type: str
    scope: str
    description: str

    def format(self) -> str:
        """Return the commit as `type(scope): description`."""
        return f"{self.type}({self.scope}): {self.description}"
