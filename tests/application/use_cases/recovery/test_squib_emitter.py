"""Round-trip tests for SquibEmitter against the real §Notation parser."""

from squeaky_clean.application.use_cases.parse_architecture_notation import (
    ParseArchitectureNotation,
)
from squeaky_clean.application.use_cases.recovery.squib_emitter import SquibEmitter
from squeaky_clean.domain.entities.architecture_graph import ArchitectureGraph
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType

_EVENT = ClassSpec(
    name="IngestedEvent", pattern="Entity", implements=None,
    methods=("validate(): bool",), depends=(), concretes=(),
    fields=("id: str", "payload: str"),
)
_PORT = ClassSpec(
    name="ProducerPort", pattern="Gateway", implements=None,
    methods=("publish_event(event: IngestedEvent): None",),
    depends=("Ingest::IngestedEvent",), concretes=(), fields=(),
)
_INGEST = ModuleSpec(
    name="Ingest", layer=LayerType.DOMAIN, exports=("IngestedEvent",),
    depends=(), classes=(_EVENT,), invariants=(),
)
_FORWARDING = ModuleSpec(
    name="Forwarding", layer=LayerType.APPLICATION, exports=("ProducerPort",),
    depends=("Ingest::IngestedEvent",), classes=(_PORT,), invariants=(),
)
_SPEC = ArchitectureSpec(
    modules=(_INGEST, _FORWARDING),
    graph=ArchitectureGraph(edges={"Forwarding": ("Ingest",)}),
)


def _round_trip(spec: ArchitectureSpec) -> ArchitectureSpec:
    return ParseArchitectureNotation().parse(SquibEmitter().emit(spec))


def test_modules_round_trip_identically() -> None:
    assert _round_trip(_SPEC).modules == _SPEC.modules


def test_cross_module_graph_edges_are_reconstructed() -> None:
    # The parser canonicalizes edges to key every module (empty deps for
    # those with no cross-module DEPENDS), so Ingest appears with ().
    assert _round_trip(_SPEC).graph.edges == {
        "Forwarding": ("Ingest",), "Ingest": (),
    }


def test_single_module_round_trips() -> None:
    spec = ArchitectureSpec.single(_INGEST)
    assert _round_trip(spec).modules == (_INGEST,)


def test_emitted_text_is_valid_and_parseable() -> None:
    text = SquibEmitter().emit(_SPEC)
    assert text.startswith("MODULE Ingest")
    assert "LAYER Domain" in text
    assert _round_trip(_SPEC).validate() == ()
