"""Tests for SelfLayerClassifier: provisional layer from own AST signals."""

from squeaky_clean.application.generation.recovery.decomposition.self_layer_classifier import (
    SelfLayerClassifier,
)
from squeaky_clean.application.generation.recovery.extraction.class_record import ClassRecord
from squeaky_clean.domain.value_objects.layer_type import LayerType


def _record(
    methods: tuple[str, ...] = (), decorators: tuple[str, ...] = (),
) -> ClassRecord:
    return ClassRecord(
        fqn="p.C", bases=(), methods=methods, fields=(),
        imports=(), decorators=decorators,
    )


def test_route_decorator_classifies_interface() -> None:
    record = _record(decorators=("app.route('/users')",))
    assert SelfLayerClassifier().classify(record) == LayerType.INTERFACE


def test_rest_controller_annotation_is_case_insensitive_interface() -> None:
    record = _record(decorators=("RestController",))
    assert SelfLayerClassifier().classify(record) == LayerType.INTERFACE


def test_infrastructure_verbs_classify_infrastructure() -> None:
    record = _record(methods=("save(entity)", "find_by_id(id)"))
    assert SelfLayerClassifier().classify(record) == LayerType.INFRASTRUCTURE


def test_plain_business_class_defaults_to_domain() -> None:
    record = _record(methods=("total()",))
    assert SelfLayerClassifier().classify(record) == LayerType.DOMAIN
