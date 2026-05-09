"""NotationClassBlockIterator: yield class entries from a CLASSES body."""

from collections.abc import Iterator

from squeaky_clean.application.use_cases.notation_brace_scanner import NotationBraceScanner
from squeaky_clean.domain.entities.notation_parse_error import NotationParseError


class NotationClassBlockIterator:
    """Iterates `(header, inner)` pairs for every class in a CLASSES body."""

    def __init__(self) -> None:
        self._scanner: NotationBraceScanner = NotationBraceScanner()

    def iterate(self, body: str) -> Iterator[tuple[str, str]]:
        """Yield (header_text, inner_text) for each class entry."""
        idx = 0
        while idx < len(body):
            while idx < len(body) and body[idx].isspace():
                idx += 1
            if idx >= len(body):
                return
            brace = body.find("{", idx)
            if brace == -1:
                raise NotationParseError("class entry missing '{'")
            header = body[idx:brace].strip()
            inner, end = self._scanner.inside_brace(body, brace)
            idx = end
            yield header, inner
