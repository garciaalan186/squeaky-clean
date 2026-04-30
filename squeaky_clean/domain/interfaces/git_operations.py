"""GitOperations port: abstract interface for worktree + commit operations."""

from abc import ABC, abstractmethod
from pathlib import Path

from squeaky_clean.domain.value_objects.conventional_commit import ConventionalCommit


class GitOperations(ABC):
    """Port for creating worktrees, committing, and merging worktrees back."""

    @abstractmethod
    def create_worktree(self, name: str) -> Path:
        """Create a new worktree and return its path."""

    @abstractmethod
    def commit(self, message: ConventionalCommit) -> str:
        """Commit staged changes with the given message; return the commit SHA."""

    @abstractmethod
    def merge_worktree(self, name: str) -> None:
        """Merge the named worktree back into the main branch."""
