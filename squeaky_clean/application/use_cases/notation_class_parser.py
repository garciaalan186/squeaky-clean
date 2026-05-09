"""NotationClassParser: parse the body of a §Notation CLASSES block."""

from squeaky_clean.application.use_cases.notation_class_block_iterator import (
    NotationClassBlockIterator,
)
from squeaky_clean.application.use_cases.notation_field_parser import NotationFieldParser
from squeaky_clean.application.use_cases.notation_invariants_parser import (
    NotationInvariantsParser,
)
from squeaky_clean.application.use_cases.notation_list_splitter import NotationListSplitter
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.notation_parse_error import NotationParseError
from squeaky_clean.domain.value_objects.pattern_name import ALL_PATTERNS


class NotationClassParser:
    """Parses the inside of a `CLASSES { ... }` block into ClassSpec list."""

    def __init__(self) -> None:
        self._blocks: NotationClassBlockIterator = NotationClassBlockIterator()
        self._fields: NotationFieldParser = NotationFieldParser()
        self._split: NotationListSplitter = NotationListSplitter()
        self._invars: NotationInvariantsParser = NotationInvariantsParser()

    def parse(self, body: str) -> tuple[ClassSpec, ...]:
        """Return the tuple of ClassSpec entries declared in body."""
        specs = [
            self._build_spec(header, inner)
            for header, inner in self._blocks.iterate(body)
        ]
        return tuple(specs)

    def _build_spec(self, header: str, inner: str) -> ClassSpec:
        if "->" not in header:
            raise NotationParseError(f"class header missing '->': {header!r}")
        name_part, pattern_part = header.split("->", 1)
        pattern = pattern_part.strip()
        if pattern not in ALL_PATTERNS:
            raise NotationParseError(f"unknown pattern: {pattern!r}")
        fields = self._fields.parse(inner)
        return ClassSpec(
            name=name_part.strip(),
            pattern=pattern,
            implements=fields.get("implements"),
            methods=self._split.method_tuple(fields.get("methods", "")),
            depends=self._split.plain_tuple(fields.get("depends", "")),
            concretes=self._split.plain_tuple(fields.get("concretes", "")),
            fields=self._split.plain_tuple(fields.get("fields", "")),
            invariants=self._invars.parse(fields.get("invariants", "")),
        )
