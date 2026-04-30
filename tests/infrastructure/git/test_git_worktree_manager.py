"""Tests for GitWorktreeManager — instantiation only (full flow deferred)."""

from pathlib import Path

from squeaky_clean.domain.interfaces.git_operations import GitOperations
from squeaky_clean.infrastructure.git.git_worktree_manager import GitWorktreeManager


def test_git_worktree_manager_implements_port(tmp_path: Path) -> None:
    mgr = GitWorktreeManager(tmp_path)
    assert isinstance(mgr, GitOperations)


def test_git_worktree_manager_stores_repo_path(tmp_path: Path) -> None:
    mgr = GitWorktreeManager(tmp_path)
    # Private field access is fine in a unit test. Worktree flow is
    # deferred to Phase 6; for now we only assert the constructor holds
    # the path it was given.
    assert mgr._repo == tmp_path
