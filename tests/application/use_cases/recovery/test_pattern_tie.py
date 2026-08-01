"""Tests for PatternTie: the unresolved classification value object."""

from squeaky_clean.application.generation.recovery.extraction.class_record import ClassRecord
from squeaky_clean.application.generation.recovery.scoring.tiebreak.pattern_tie import PatternTie
from squeaky_clean.domain.value_objects.layer_type import LayerType

_RECORD = ClassRecord(
    fqn="app.OrderPlacedEvent", bases=(), methods=("at()",),
    fields=("id: str",), imports=(), decorators=(),
)


def test_carries_record_layer_and_candidates() -> None:
    tie = PatternTie(record=_RECORD, layer=LayerType.DOMAIN,
                     candidates=("DomainEvent", "Entity"))
    assert tie.record is _RECORD
    assert tie.layer is LayerType.DOMAIN
    assert tie.candidates == ("DomainEvent", "Entity")


def test_is_a_frozen_value_object() -> None:
    tie = PatternTie(record=_RECORD, layer=LayerType.DOMAIN,
                     candidates=("DomainEvent", "Entity"))
    assert tie == PatternTie(record=_RECORD, layer=LayerType.DOMAIN,
                             candidates=("DomainEvent", "Entity"))
    try:
        tie.layer = LayerType.APPLICATION  # type: ignore[misc]
        raised = False
    except AttributeError:
        raised = True
    assert raised
