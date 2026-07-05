"""Tests for the deterministic PatternScorer fingerprints (Stage 3)."""

from squeaky_clean.application.dtos.recovery.class_record import ClassRecord
from squeaky_clean.application.use_cases.recovery.pattern_scorer import PatternScorer
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.pattern_name import PatternName


def _rec(
    name: str,
    methods: tuple[str, ...] = (),
    fields: tuple[str, ...] = (),
    bases: tuple[str, ...] = (),
) -> ClassRecord:
    return ClassRecord(
        fqn=f"app.{name}", bases=bases, methods=methods,
        fields=fields, imports=(), decorators=(),
    )


def _score(record: ClassRecord, layer: LayerType) -> dict[PatternName, int]:
    return PatternScorer().score(record, layer)


def test_entity_from_id_field() -> None:
    scores = _score(_rec("Order", methods=("total()",), fields=("id: str",)), LayerType.DOMAIN)
    assert scores == {"Entity": 3}


def test_value_object_when_no_id() -> None:
    scores = _score(_rec("Money", fields=("amount: int",)), LayerType.DOMAIN)
    assert scores == {"ValueObject": 2}


def test_domain_event_and_entity_tie() -> None:
    rec = _rec("OrderPlacedEvent", methods=("at()",), fields=("id: str",))
    assert _score(rec, LayerType.DOMAIN) == {"DomainEvent": 3, "Entity": 3}


def test_repository_from_persistence_verbs() -> None:
    rec = _rec("OrderRepo", methods=("save(o)", "find_by_id(i)"))
    assert _score(rec, LayerType.INFRASTRUCTURE) == {"Repository": 3}


def test_gateway_from_remote_verbs() -> None:
    assert _score(_rec("Bus", methods=("publish(e)",)), LayerType.INFRASTRUCTURE) == {"Gateway": 3}


def test_adapter_fallback_when_infra_has_base() -> None:
    rec = _rec("S3Store", methods=("stash(x)",), bases=("BlobPort",))
    assert _score(rec, LayerType.INFRASTRUCTURE) == {"Adapter": 2}


def test_use_case_from_execute_verb() -> None:
    assert _score(_rec("PlaceOrder", methods=("execute(c)",)), LayerType.APPLICATION) == {"UseCase": 3}


def test_presenter_from_render_verb() -> None:
    assert _score(_rec("OrderView", methods=("render(o)",)), LayerType.INTERFACE) == {"Presenter": 2}


def test_no_fingerprint_scores_empty() -> None:
    rec = _rec("Helper", methods=("foo()", "bar()"))
    assert _score(rec, LayerType.APPLICATION) == {}
