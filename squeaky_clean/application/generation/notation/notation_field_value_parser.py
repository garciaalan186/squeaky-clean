"""NotationFieldValueParser: parse one field body per its schema kind."""

from squeaky_clean.application.generation.notation.notation_invariants_parser import (
    NotationInvariantsParser,
)
from squeaky_clean.application.generation.notation.notation_list_splitter import (
    NotationListSplitter,
)
from squeaky_clean.domain.value_objects.notation.notation_section_spec import NotationKind


class NotationFieldValueParser:
    """Applies a SQUIB_SCHEMA-declared kind to a raw §Notation body.

    The grammar row (NotationSectionSpec / NotationClassFieldSpec) says
    WHAT a field is; this parser is the single place that maps each kind
    to HOW its text is split (R6.1c).
    """

    def __init__(self) -> None:
        self._split: NotationListSplitter = NotationListSplitter()
        self._invars: NotationInvariantsParser = NotationInvariantsParser()

    def sequence(self, raw: str, kind: NotationKind) -> tuple[str, ...]:
        """Parse a list-kinded body; non-sequence kinds are a caller bug."""
        if kind == "method_list":
            return self._split.method_tuple(raw)
        if kind == "invariant_list":
            return self._invars.parse(raw)
        if kind == "name_list":
            return self._split.plain_tuple(raw)
        raise ValueError(f"not a sequence kind: {kind}")
