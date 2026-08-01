"""NotationClassFieldSpec: one class-entry field's grammar row."""

from dataclasses import dataclass

from squeaky_clean.domain.value_objects.notation.notation_section_spec import NotationKind


@dataclass(frozen=True)
class NotationClassFieldSpec:
    """Grammar row for one `key:` field inside a CLASSES entry (R6.1c).

    ``kind`` selects how the raw body text is parsed (plain name list,
    method-signature list, quoted invariant list, or bare scalar).
    """

    name: str
    kind: NotationKind
