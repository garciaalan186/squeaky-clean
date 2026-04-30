"""Tests for GitOperations ABC."""

from pathlib import Path

import pytest

from squeaky_clean.domain.interfaces.git_operations import GitOperations
from squeaky_clean.domain.value_objects.conventional_commit import ConventionalCommit


class _StubGit(GitOperations):
    def create_worktree(self, name: str) -> Path:
        return Path(f"/tmp/wt/{name}")

    def commit(self, message: ConventionalCommit) -> str:
        return message.format()

    def merge_worktree(self, name: str) -> None:
        return None


def test_git_operations_cannot_be_instantiated_directly() -> None:
    with pytest.raises(TypeError):
        GitOperations()  # type: ignore[abstract]


def test_git_operations_stub_round_trips() -> None:
    g = _StubGit()
    assert g.create_worktree("wt1") == Path("/tmp/wt/wt1")
    commit = ConventionalCommit(type="feat", scope="X", description="d")
    assert g.commit(commit) == "feat(X): d"
    g.merge_worktree("wt1")
