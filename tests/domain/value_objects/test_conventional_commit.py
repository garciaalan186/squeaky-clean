"""Tests for ConventionalCommit."""

from squeaky_clean.domain.value_objects.conventional_commit import ConventionalCommit


def test_format_produces_type_scope_description() -> None:
    commit = ConventionalCommit(
        type="feat",
        scope="RunEval",
        description="write skeleton report",
    )
    assert commit.format() == "feat(RunEval): write skeleton report"
