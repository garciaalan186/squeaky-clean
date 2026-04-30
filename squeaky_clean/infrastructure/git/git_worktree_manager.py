"""GitWorktreeManager: subprocess-backed GitOperations adapter.

Phase 4 scope note: for P0 the pipeline writes generated files directly
via ``LocalFileSystem`` and does NOT engage worktrees. This class exists
so OrchestrateModule can depend on a concrete adapter when Phase 6 (or
later) enables per-ICP worktrees, but none of its methods are wired into
the current P0 flow. Tests instantiate it and exercise the argv shape
only — full worktree plumbing is deferred.
"""

import subprocess
from pathlib import Path

from squeaky_clean.domain.interfaces.git_operations import GitOperations
from squeaky_clean.domain.value_objects.conventional_commit import ConventionalCommit


class GitWorktreeManager(GitOperations):
    """Thin ``git`` subprocess wrapper implementing the GitOperations port."""

    def __init__(self, repo_path: Path) -> None:
        self._repo: Path = repo_path

    def create_worktree(self, name: str) -> Path:
        """Create a worktree named ``name`` under ``<repo>/.worktrees``."""
        target = self._repo / ".worktrees" / name
        subprocess.run(
            ["git", "-C", str(self._repo), "worktree", "add", str(target), "-b", name],
            check=True,
        )
        return target

    def commit(self, message: ConventionalCommit) -> str:
        """Commit staged changes with ``message``; return the new commit SHA."""
        subprocess.run(
            ["git", "-C", str(self._repo), "commit", "-m", message.format()],
            check=True,
        )
        sha = subprocess.run(
            ["git", "-C", str(self._repo), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        )
        return sha.stdout.strip()

    def merge_worktree(self, name: str) -> None:
        """Merge the worktree branch ``name`` into the current HEAD."""
        subprocess.run(
            ["git", "-C", str(self._repo), "merge", "--no-ff", name],
            check=True,
        )
