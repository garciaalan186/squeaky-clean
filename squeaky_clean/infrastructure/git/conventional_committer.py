"""ConventionalCommitter: thin wrapper that renders a ConventionalCommit."""

from squeaky_clean.domain.value_objects.conventional_commit import ConventionalCommit


class ConventionalCommitter:
    """Formats a ConventionalCommit value object into its canonical string."""

    def format(self, commit: ConventionalCommit) -> str:
        """Return ``type(scope): description`` for ``commit``."""
        return commit.format()
