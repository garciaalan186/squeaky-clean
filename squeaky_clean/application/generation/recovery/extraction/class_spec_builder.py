"""ClassSpecBuilder: turn a ClassRecord into a Squib ClassSpec."""

from squeaky_clean.application.generation.recovery.extraction.class_record import ClassRecord
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.value_objects.pattern_name import PatternName


class ClassSpecBuilder:
    """Maps one recovered ClassRecord onto a ClassSpec entity.

    ``patterns`` maps class FQNs to Stage 3's classifier verdicts
    (``SimpleClass`` for unmapped classes). Methods are carried over
    verbatim. Untyped fields recovered from bare ``self.<attr>``
    assignments are given an ``: object`` annotation so the spec satisfies
    the ``name: Type`` field-shape validator; already-typed fields pass
    through unchanged. Depends are pre-rendered by the caller.
    """

    def __init__(self, patterns: dict[str, PatternName] | None = None) -> None:
        self._patterns: dict[str, PatternName] = patterns or {}

    def build(
        self, record: ClassRecord, depends: tuple[str, ...],
    ) -> ClassSpec:
        """Return the ClassSpec for one record with rendered dependencies."""
        return ClassSpec(
            name=record.fqn.rsplit(".", 1)[-1],
            pattern=self._patterns.get(record.fqn, "SimpleClass"),
            implements=None,
            methods=record.methods,
            depends=depends,
            concretes=(),
            fields=tuple(self._typed(f) for f in record.fields),
            invariants=(),
        )

    def _typed(self, field: str) -> str:
        return field if ":" in field else f"{field}: object"
