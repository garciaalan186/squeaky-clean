"""H5b: derive_required_categories now recognises seven new categories."""

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
        name=name, pattern="Adapter", implements=None,
        methods=methods, depends=(), concretes=(),
    )


def test_rest_server_handler_inferred_from_handle() -> None:
    arch = _arch(_module(LayerType.INFRASTRUCTURE, (
        _cls("OrderHttp", ("handle(payload: dict): dict",)),
    )))
    assert derive_required_categories(arch) == frozenset(
        {"rest_server_handler"}
    )


def test_grpc_client_inferred_from_call() -> None:
    arch = _arch(_module(LayerType.INFRASTRUCTURE, (
        _cls("OrderClient", ("call(method: str, request: bytes): bytes",
                             "close(): None")),
    )))
    assert derive_required_categories(arch) == frozenset({"grpc_client"})


def test_grpc_server_handler_inferred_from_serve() -> None:
    arch = _arch(_module(LayerType.INFRASTRUCTURE, (
        _cls("OrderRpc", ("serve(request: dict): dict",)),
    )))
    assert derive_required_categories(arch) == frozenset(
        {"grpc_server_handler"}
    )


def test_websocket_inferred_from_on_message() -> None:
    arch = _arch(_module(LayerType.INFRASTRUCTURE, (
        _cls("ChatWs", ("on_message(msg: dict): dict",
                        "accept_connection(client_id: str): dict")),
    )))
    assert derive_required_categories(arch) == frozenset(
        {"websocket_server_handler"}
    )


def test_observability_logger_inferred_from_info_warn_error() -> None:
    arch = _arch(_module(LayerType.INFRASTRUCTURE, (
        _cls("AppLogger", ("info(event: str, context: dict): None",
                           "warn(event: str, context: dict): None",
                           "error(event: str, context: dict): None")),
    )))
    assert derive_required_categories(arch) == frozenset(
        {"observability_logger"}
    )


def test_secrets_provider_inferred_from_get_put_secret() -> None:
    arch = _arch(_module(LayerType.INFRASTRUCTURE, (
        _cls("Vault", ("get_secret(name: str): str",
                       "put_secret(name: str, value: str): None")),
    )))
    assert derive_required_categories(arch) == frozenset(
        {"secrets_provider"}
    )


def test_search_inferred_from_index_query() -> None:
    arch = _arch(_module(LayerType.INFRASTRUCTURE, (
        _cls("Es", ("index(doc_id: str, body: dict): None",
                    "query(q: dict): list")),
    )))
    assert derive_required_categories(arch) == frozenset({"search"})
