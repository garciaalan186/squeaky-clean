"""Tests for ConventionalCommitter formatter."""

from squeaky_clean.domain.value_objects.conventional_commit import ConventionalCommit
from squeaky_clean.infrastructure.git.conventional_committer import ConventionalCommitter


def test_format_produces_canonical_message() -> None:
    committer = ConventionalCommitter()
    commit = ConventionalCommit(
        type="feat",
        scope="Calculator",
        description="add divide",
    )
    assert committer.format(commit) == "feat(Calculator): add divide"


def test_format_preserves_fields() -> None:
    committer = ConventionalCommitter()
    commit = ConventionalCommit(type="fix", scope="Money", description="rounding")
    assert committer.format(commit) == "fix(Money): rounding"
