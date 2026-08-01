"""Tests for wiring_walker: adapter/use-case extraction + categorization."""

from squeaky_clean.application.generation.integration.wiring_walker import (
    adapters,
    category_for,
    first_with_category,
    split_inbound,
    use_cases,
)
from squeaky_clean.domain.entities.architecture_graph import ArchitectureGraph
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.pattern_name import PatternName


def _cls(name: str, pattern: PatternName,
         methods: tuple[str, ...] = ()) -> ClassSpec:
    return ClassSpec(name=name, pattern=pattern, implements=None,
                     methods=methods, depends=(), concretes=())


def _mod(name: str, layer: LayerType,
         classes: tuple[ClassSpec, ...]) -> ModuleSpec:
    return ModuleSpec(name=name, layer=layer, exports=(), depends=(),
                      classes=classes, invariants=())


_PUBLISHER = _cls("EventPublisher", "Adapter", ("publish_event(e: str): None",))
_HANDLER = _cls("OrderController", "Adapter", ("handle(req: str): str",))
_ARCH = ArchitectureSpec(
    modules=(
        _mod("Orders", LayerType.DOMAIN, (_cls("Order", "Entity"),)),
        _mod("Checkout", LayerType.APPLICATION,
             (_cls("PlaceOrder", "UseCase"), _cls("OrderId", "ValueObject"))),
        _mod("Messaging", LayerType.INFRASTRUCTURE, (_PUBLISHER,)),
        _mod("Web", LayerType.INTERFACE, (_HANDLER,)),
    ),
    graph=ArchitectureGraph(edges={}),
)


def test_adapters_come_only_from_infrastructure_and_interface_layers() -> None:
    found = adapters(_ARCH)
    assert [(m.name, c.name) for m, c in found] == [
        ("Messaging", "EventPublisher"), ("Web", "OrderController"),
    ]


def test_use_cases_come_only_from_application_layer() -> None:
    assert [(m.name, c.name) for m, c in use_cases(_ARCH)] == [
        ("Checkout", "PlaceOrder"),
    ]


def test_category_for_infers_from_method_verbs_or_returns_empty() -> None:
    assert category_for(_PUBLISHER) == "message_queue_producer"
    assert category_for(_HANDLER) == "rest_server_handler"
    assert category_for(_cls("Order", "Entity")) == ""


def test_split_inbound_and_first_with_category_partition_adapters() -> None:
    found = adapters(_ARCH)
    outbound, inbound = split_inbound(found)
    assert [c.name for _m, c in outbound] == ["EventPublisher"]
    assert [c.name for _m, c in inbound] == ["OrderController"]
    match = first_with_category(found, "rest_server_handler")
    assert match is not None and match.name == "OrderController"
    assert first_with_category(found, "kv_cache") is None
