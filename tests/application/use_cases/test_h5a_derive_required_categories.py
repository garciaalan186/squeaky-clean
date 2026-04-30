"""H5a: derive_required_categories now recognises five new categories."""

from squeaky_clean.application.use_cases.derive_required_categories import (
    derive_required_categories,
)
from squeaky_clean.domain.entities.architecture_graph import ArchitectureGraph
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType


def _module(layer: LayerType, classes: tuple[ClassSpec, ...]) -> ModuleSpec:
    return ModuleSpec(
        name="M", layer=layer, exports=(), depends=(),
        classes=classes, invariants=(),
    )


def _arch(*modules: ModuleSpec) -> ArchitectureSpec:
    return ArchitectureSpec(
        modules=tuple(modules), graph=ArchitectureGraph(edges={}),
    )


def _cls(name: str, methods: tuple[str, ...]) -> ClassSpec:
    return ClassSpec(
        name=name, pattern="Repository", implements=None,
        methods=methods, depends=(), concretes=(),
    )


def test_relational_db_inferred_from_save_find_by_id() -> None:
    arch = _arch(_module(LayerType.INFRASTRUCTURE, (
        _cls("OrdersRepo", ("save(id: str, body: bytes): None",
                            "find_by_id(id: str): bytes")),
    )))
    assert derive_required_categories(arch) == frozenset({"relational_db"})


def test_document_db_inferred_from_upsert() -> None:
    arch = _arch(_module(LayerType.INFRASTRUCTURE, (
        _cls("DocsRepo", ("upsert(id: str, body: bytes): None",
                          "find_by_id(id: str): bytes")),
    )))
    assert derive_required_categories(arch) == frozenset({"document_db"})


def test_mq_producer_inferred_from_publish() -> None:
    arch = _arch(_module(LayerType.INFRASTRUCTURE, (
        _cls("EventOut", ("publish(topic: str, payload: bytes): None",
                          "flush(timeout: float): None")),
    )))
    assert derive_required_categories(arch) == frozenset({"message_queue_producer"})


def test_mq_consumer_inferred_from_consume() -> None:
    arch = _arch(_module(LayerType.INFRASTRUCTURE, (
        _cls("EventIn", ("consume(queue: str): bytes",
                         "close(): None")),
    )))
    assert derive_required_categories(arch) == frozenset({"message_queue_consumer"})


def test_stream_processor_inferred_from_process_aggregate() -> None:
    arch = _arch(_module(LayerType.INFRASTRUCTURE, (
        _cls("StreamGW", ("process(record: bytes): bytes",
                          "aggregate(window: int): bytes")),
    )))
    assert derive_required_categories(arch) == frozenset({"stream_processor"})
