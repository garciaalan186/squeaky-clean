"""Tests for wiring_construction: per-class ctor-line emitters."""

from squeaky_clean.application.generation.integration.wiring_construction import (
    emit_inbound,
    emit_outbound,
    emit_use_case,
)
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.value_objects.pattern_name import PatternName
from squeaky_clean.domain.value_objects.tech_spec import TechSpec
from squeaky_clean.domain.value_objects.tech_spec_operation import TechSpecOperation


def _cls(name: str, pattern: PatternName, methods: tuple[str, ...] = (),
         depends: tuple[str, ...] = ()) -> ClassSpec:
    return ClassSpec(name=name, pattern=pattern, implements=None,
                     methods=methods, depends=depends, concretes=())


def _tech(category: str, deps: list[str]) -> TechSpec:
    return TechSpec(
        schema_version="v1", category=category, technology="t",
        version_pin="1", language="python",
        install={"manager": "pip", "package": "p==1"},
        imports={"primary": "p"},
        client_construction={"code": "x", "dependencies": deps},
        primary_operations=(TechSpecOperation(
            name="op", signature="()", sdk_call="c",
            error_types=("E",), idempotency="idempotent"),),
        auth={"method": "none"})


def test_emit_outbound_uses_env_args_and_registers_symbol() -> None:
    publisher = _cls("EventPublisher", "Adapter", methods=("publish_event(e: str): None",))
    symbols: dict[str, str] = {}
    line = emit_outbound(publisher, {"message_queue_producer": _tech(
        "message_queue_producer", ["broker_url"])}, symbols)
    assert line == 'event_publisher = EventPublisher(os.environ.get("BROKER_URL", ""))'
    assert symbols == {"EventPublisher": "event_publisher"}


def test_emit_outbound_without_tech_spec_leaves_todo_placeholder() -> None:
    publisher = _cls("EventPublisher", "Adapter", methods=("publish_event(e: str): None",))
    line = emit_outbound(publisher, {}, {})
    assert line.startswith('event_publisher = EventPublisher(""')
    assert "TODO" in line


def test_emit_use_case_wires_only_resolvable_dependencies() -> None:
    use_case = _cls("PlaceOrder", "UseCase", depends=("EventPublisher", "Unwired"))
    symbols = {"EventPublisher": "event_publisher"}
    line = emit_use_case(use_case, symbols)
    assert line == "place_order = PlaceOrder(event_publisher)"
    assert symbols["PlaceOrder"] == "place_order"


def test_emit_inbound_appends_env_vars_after_use_case_dep() -> None:
    controller = _cls("OrderController", "Adapter",
                      methods=("handle(req: str): str",), depends=("PlaceOrder",))
    symbols = {"PlaceOrder": "place_order"}
    line = emit_inbound(controller, {"rest_server_handler": _tech(
        "rest_server_handler", ["use_case", "host"])}, symbols)
    assert line == ('order_controller = OrderController('
                    'place_order, os.environ.get("HOST", ""))')
