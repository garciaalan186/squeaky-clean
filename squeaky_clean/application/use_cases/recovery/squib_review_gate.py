"""SquibReviewGate: emit a Squib for human sign-off and reload the edits."""

import re
from pathlib import Path

from squeaky_clean.application.use_cases.parse_architecture_notation import (
    ParseArchitectureNotation,
)
from squeaky_clean.application.use_cases.recovery.squib_emitter import SquibEmitter
from squeaky_clean.application.use_cases.recovery.squib_review_error import (
    SquibReviewError,
)
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.notation_parse_error import NotationParseError

_QUOTED = re.compile(r"'([^']+)'")


class SquibReviewGate:
    """Stage 5: write the recovered Squib for review, reload after sign-off.

    ``emit`` renders the ArchitectureSpec to a file the human reads and
    edits. ``load`` reparses that file: on success it returns the
    signed-off spec; on failure it raises SquibReviewError pinpointing the
    offending line so the pipeline can report it and wait for a corrected
    version. The gate never regenerates — it only brackets the human step.
    """

    def __init__(self) -> None:
        self._emitter: SquibEmitter = SquibEmitter()
        self._parser: ParseArchitectureNotation = ParseArchitectureNotation()

    def emit(self, spec: ArchitectureSpec, path: Path) -> None:
        """Write the recovered architecture to ``path`` as editable Squib."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self._emitter.emit(spec))

    def load(self, path: Path) -> ArchitectureSpec:
        """Reparse the human-edited Squib; raise with line context on error."""
        text = path.read_text()
        try:
            return self._parser.parse(text)
        except NotationParseError as exc:
            line, snippet = self._locate(text, str(exc))
            raise SquibReviewError(str(exc), line, snippet) from exc

    def _locate(self, text: str, message: str) -> tuple[int | None, str]:
        match = _QUOTED.search(message)
        if match is not None:
            token = match.group(1)
            for number, line in enumerate(text.splitlines(), start=1):
                if token in line:
                    return number, line.strip()
        return None, ""
