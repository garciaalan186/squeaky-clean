"""H5b routing tests for MapPatternToEmitter and infrastructure_category_inference.

Covers rest_server_handler, grpc_client, grpc_server_handler,
websocket_server_handler, observability_logger, secrets_provider, and search.
"""

from squeaky_clean.application.generation.emission.map_pattern_to_emitter import MapPatternToEmitter
from squeaky_clean.application.generation.techspec.infrastructure_category_inference import (
    infer_category,
)
from squeaky_clean.application.shared.language.language_toolkit_factory import (
    LanguageToolkitFactory,
)
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.pattern_name import PatternName
from squeaky_clean.domain.value_objects.target_language import TargetLanguage

_PY = LanguageToolkitFactory().for_language(TargetLanguage.PYTHON)


def _icp(
    pattern: PatternName, layer: LayerType, methods: tuple[str, ...],
    mode: str = "auto",
) -> str:
    cls = ClassSpec(
        name="Subject", pattern=pattern, implements=None,
        methods=methods, depends=(), concretes=(),
    )
    module = ModuleSpec(
        name="M", layer=layer, exports=(), depends=(),
        classes=(cls,), invariants=(),
    )
    return MapPatternToEmitter(_PY, infrastructure_mode=mode).map_for(cls, module)


def test_rest_server_handler_routes_when_handle_present() -> None:
    # rest_server_handler lives in INTERFACE layer (HTTP entry point).
    icp = _icp("Adapter", LayerType.INTERFACE, ("handle",))
    assert icp == "python/infrastructure/RestServerHandlerEmitter"


def test_rest_server_handler_routes_when_route_present() -> None:
    icp = _icp("Adapter", LayerType.INTERFACE, ("route",))
    assert icp == "python/infrastructure/RestServerHandlerEmitter"


def test_grpc_client_routes_when_invoke_present() -> None:
    icp = _icp("Adapter", LayerType.INFRASTRUCTURE, ("invoke", "close"))
    assert icp == "python/infrastructure/GrpcClientEmitter"


def test_grpc_client_routes_when_call_present() -> None:
    icp = _icp("Adapter", LayerType.INFRASTRUCTURE, ("call", "close"))
    assert icp == "python/infrastructure/GrpcClientEmitter"


def test_grpc_server_handler_routes_when_serve_present() -> None:
    icp = _icp("Adapter", LayerType.INTERFACE, ("serve",))
    assert icp == "python/infrastructure/GrpcServerHandlerEmitter"


def test_grpc_server_handler_routes_when_handle_request_present() -> None:
    icp = _icp("Adapter", LayerType.INTERFACE, ("handle_request",))
    assert icp == "python/infrastructure/GrpcServerHandlerEmitter"


def test_websocket_server_routes_when_on_message_present() -> None:
    icp = _icp("Adapter", LayerType.INTERFACE, ("on_message", "accept_connection"))
    assert icp == "python/infrastructure/WebSocketServerHandlerEmitter"


def test_observability_logger_routes_when_info_warn_error_present() -> None:
    icp = _icp("Gateway", LayerType.INFRASTRUCTURE, ("info", "warn", "error"))
    assert icp == "python/infrastructure/ObservabilityLoggerEmitter"


def test_secrets_provider_routes_when_get_secret_present() -> None:
    icp = _icp("Gateway", LayerType.INFRASTRUCTURE, ("get_secret", "put_secret"))
    assert icp == "python/infrastructure/SecretsProviderEmitter"


def test_search_routes_when_index_query_present() -> None:
    icp = _icp("Gateway", LayerType.INFRASTRUCTURE, ("index", "query"))
    assert icp == "python/infrastructure/SearchEmitter"


def test_search_routes_when_search_method_present() -> None:
    icp = _icp("Gateway", LayerType.INFRASTRUCTURE, ("search",))
    assert icp == "python/infrastructure/SearchEmitter"


def test_h5b_categories_fall_back_when_manual() -> None:
    icp = _icp(
        "Gateway", LayerType.INFRASTRUCTURE, ("get_secret",), mode="manual",
    )
    # Manual mode skips Tier C and falls back to the legacy map(), which
    # routes an abstract Gateway port to the (interface-emitting) GatewayEmitter.
    assert icp == "python/ddd_clean/GatewayEmitter"


def test_secrets_beats_search_get_when_get_secret_present() -> None:
    """Order-sensitivity: get_secret is more specific than bare 'get'."""
    assert (
        infer_category(("get_secret", "put_secret")) == "secrets_provider"
    )


def test_grpc_server_beats_grpc_client_when_serve_method_present() -> None:
    """Order-sensitivity: serve (server) wins over call (client) for hybrid specs."""
    assert (
        infer_category(("serve", "call")) == "grpc_server_handler"
    )
