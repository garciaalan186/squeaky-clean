"""Tests for PatternClassifier tie handling (Stage 3)."""

from squeaky_clean.application.dtos.recovery.class_catalog import ClassCatalog
from squeaky_clean.application.dtos.recovery.class_record import ClassRecord
from squeaky_clean.application.use_cases.recovery.pattern_classifier import PatternClassifier
from squeaky_clean.application.use_cases.recovery.pattern_tiebreak import PatternTiebreak
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.pattern_name import PatternName


class _FakeTiebreak(PatternTiebreak):
    def __init__(self, choice: PatternName) -> None:
        self._choice: PatternName = choice
        self.calls: int = 0
        self.seen: tuple[PatternName, ...] = ()

    def resolve(
        self, record: ClassRecord, layer: LayerType,
        candidates: tuple[PatternName, ...],
    ) -> PatternName:
        self.calls += 1
        self.seen = candidates
        return self._choice


def _rec(name: str, methods: tuple[str, ...], fields: tuple[str, ...]) -> ClassRecord:
    return ClassRecord(
        fqn=f"app.{name}", bases=(), methods=methods,
        fields=fields, imports=(), decorators=(),
    )


_ENTITY = _rec("Order", ("total()",), ("id: str",))
_TIE = _rec("OrderPlacedEvent", ("at()",), ("id: str",))
_PLAIN = _rec("Helper", ("foo()", "bar()"), ())


def _classify(record: ClassRecord, layer: LayerType, tb: PatternTiebreak | None) -> str:
    catalog = ClassCatalog(classes=(record,), import_graph={record.fqn: ()})
    return PatternClassifier(tb).classify_all(catalog, {record.fqn: layer})[record.fqn]


def test_unique_winner_selected() -> None:
    assert _classify(_ENTITY, LayerType.DOMAIN, None) == "Entity"


def test_no_score_is_simple_class() -> None:
    assert _classify(_PLAIN, LayerType.APPLICATION, None) == "SimpleClass"


def test_tie_without_tiebreak_falls_back_to_simple_class() -> None:
    assert _classify(_TIE, LayerType.DOMAIN, None) == "SimpleClass"


def test_tie_consults_tiebreak_with_candidate_set() -> None:
    fake = _FakeTiebreak("Entity")
    result = _classify(_TIE, LayerType.DOMAIN, fake)
    assert result == "Entity"
    assert fake.calls == 1
    assert fake.seen == ("DomainEvent", "Entity")


def test_no_tie_never_consults_tiebreak() -> None:
    fake = _FakeTiebreak("ValueObject")
    _classify(_ENTITY, LayerType.DOMAIN, fake)
    assert fake.calls == 0
