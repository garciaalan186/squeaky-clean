"""Tests for the PatternTiebreak port contract."""

from squeaky_clean.application.generation.recovery.extraction.class_record import ClassRecord
from squeaky_clean.application.generation.recovery.scoring.tiebreak.pattern_tie import PatternTie
from squeaky_clean.application.generation.recovery.scoring.tiebreak.pattern_tiebreak import (
    PatternTiebreak,
)
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.pattern_name import PatternName


class _FirstCandidate(PatternTiebreak):
    def resolve(self, tie: PatternTie) -> PatternName:
        return tie.candidates[0]


def test_is_abstract() -> None:
    try:
        PatternTiebreak()  # type: ignore[abstract]
        instantiated = True
    except TypeError:
        instantiated = False
    assert not instantiated


def test_concrete_adapter_resolves_from_the_tie() -> None:
    record = ClassRecord(fqn="app.Order", bases=(), methods=(), fields=(),
                         imports=(), decorators=())
    tie = PatternTie(record=record, layer=LayerType.DOMAIN,
                     candidates=("Entity", "ValueObject"))
    assert _FirstCandidate().resolve(tie) == "Entity"
