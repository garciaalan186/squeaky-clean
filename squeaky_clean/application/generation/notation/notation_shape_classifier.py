"""NotationShapeClassifier: flag Squib constructions the corpus has not seen."""

from __future__ import annotations

from pathlib import Path

from squeaky_clean.application.generation.notation.parse_architecture_notation import (
    ParseArchitectureNotation,
)
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.value_objects.notation.notation_schema import SQUIB_SCHEMA


def _signature(c: ClassSpec) -> str:
    """Shape of one class construction: pattern + which fields it uses.

    Bit order is SQUIB_SCHEMA's class-field order (R6.1c) — the schema,
    not this module, owns the grammar's field list.
    """
    presence = c.notation_presence()
    bits = "".join(
        "1" if presence[name] else "0"
        for name in SQUIB_SCHEMA.class_field_names()
    )
    return f"{c.pattern}:{bits}"


class NotationShapeClassifier:
    """Corpus-driven novelty check over architect-emitted Squibs (R5.5).

    "Known" is DEFINED by eval/squib_fixtures: every (pattern, field-usage)
    shape appearing in the fixture corpus is a tested construction. A live
    Squib using a shape outside that set is NOVEL — observed and reported,
    never a failure — so notation evolution is watched deliberately instead
    of discovered as a downstream contract break (the R0.11 lesson).
    """

    def __init__(self, fixtures_dir: Path) -> None:
        self._known: frozenset[str] = self._load(fixtures_dir)

    def novel_constructions(self, arch: ArchitectureSpec) -> tuple[str, ...]:
        """Signatures in ``arch`` absent from the fixture corpus, sorted."""
        seen = {
            _signature(c) for module in arch.modules for c in module.classes
        }
        return tuple(sorted(seen - self._known))

    @staticmethod
    def _load(fixtures_dir: Path) -> frozenset[str]:
        parser = ParseArchitectureNotation()
        known: set[str] = set()
        for fixture in sorted(fixtures_dir.glob("*.squib")):
            try:
                arch = parser.parse(fixture.read_text())
            except Exception:  # noqa: BLE001 — a bad fixture never blocks runs
                continue
            for module in arch.modules:
                known.update(_signature(c) for c in module.classes)
        return frozenset(known)
