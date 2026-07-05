"""SquibReviewError: a parse failure in a human-edited Squib, with context."""

from squeaky_clean.domain.entities.notation_parse_error import NotationParseError


class SquibReviewError(NotationParseError):
    """Raised when a signed-off Squib no longer parses.

    Carries the 1-based ``line`` of the offending token (when it can be
    located in the edited document) and the ``snippet`` of that line, so
    the review loop can show the human exactly where to fix things and
    wait for a corrected version before any regeneration runs.
    """

    def __init__(self, reason: str, line: int | None, snippet: str) -> None:
        self.reason: str = reason
        self.line: int | None = line
        self.snippet: str = snippet
        location = f" (line {line}: {snippet!r})" if line is not None else ""
        super().__init__(f"{reason}{location}")
