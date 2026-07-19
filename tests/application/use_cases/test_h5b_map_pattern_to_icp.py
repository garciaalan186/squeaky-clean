"""H5b routing tests for MapPatternToICP and infrastructure_category_inference.

Adds coverage for rest_server_handler, grpc_client, grpc_server_handler,
websocket_server_handler, observability_logger, secrets_provider, and
search categories.
"""

from squeaky_clean.application.use_cases.infrastructure_category_inference import (
    infer_category,
)
from squeaky_clean.application.use_cases.language_toolkit_factory import (
    LanguageToolkitFactory,
)
from squeaky_clean.application.use_cases.map_pattern_to_icp import MapPatternToICP
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.target_language import TargetLanguage

_PY = LanguageToolkitFactory().for_language(TargetLanguage.PYTHON)


def test_rest_server_handler_routes_when_handle_present() -> None:
    # rest_server_handler lives in INTERFACE layer (HTTP entry point).
    icp = MapPatternToICP().map_with_layer(
        "Adapter", _PY, LayerType.INTERFACE,
        ("handle",),
        infrastructure_mode="auto",
    )
    assert icp == "python/infrastructure/RestServerHandlerICP"


def test_rest_server_handler_routes_when_route_present() -> None:
    icp = MapPatternToICP().map_with_layer(
        "Adapter", _PY, LayerType.INTERFACE,
        ("route",),
        infrastructure_mode="auto",
    )
    assert icp == "python/infrastructure/RestServerHandlerICP"


def test_grpc_client_routes_when_invoke_present() -> None:
    icp = MapPatternToICP().map_with_layer(
        "Adapter", _PY, LayerType.INFRASTRUCTURE,
        ("invoke", "close"),
        infrastructure_mode="auto",
    )
    assert icp == "python/infrastructure/GrpcClientICP"


def test_grpc_client_routes_when_call_present() -> None:
    icp = MapPatternToICP().map_with_layer(
        "Adapter", _PY, LayerType.INFRASTRUCTURE,
        ("call", "close"),
        infrastructure_mode="auto",
    )
    assert icp == "python/infrastructure/GrpcClientICP"


def test_grpc_server_handler_routes_when_serve_present() -> None:
    icp = MapPatternToICP().map_with_layer(
        "Adapter", _PY, LayerType.INTERFACE,
        ("serve",),
        infrastructure_mode="auto",
    )
    assert icp == "python/infrastructure/GrpcServerHandlerICP"


def test_grpc_server_handler_routes_when_handle_request_present() -> None:
    icp = MapPatternToICP().map_with_layer(
        "Adapter", _PY, LayerType.INTERFACE,
        ("handle_request",),
        infrastructure_mode="auto",
    )
    assert icp == "python/infrastructure/GrpcServerHandlerICP"


def test_websocket_server_routes_when_on_message_present() -> None:
    icp = MapPatternToICP().map_with_layer(
        "Adapter", _PY, LayerType.INTERFACE,
        ("on_message", "accept_connection"),
        infrastructure_mode="auto",
    )
    assert icp == "python/infrastructure/WebSocketServerHandlerICP"


def test_observability_logger_routes_when_info_warn_error_present() -> None:
    icp = MapPatternToICP().map_with_layer(
        "Gateway", _PY, LayerType.INFRASTRUCTURE,
        ("info", "warn", "error"),
        infrastructure_mode="auto",
    )
    assert icp == "python/infrastructure/ObservabilityLoggerICP"


def test_secrets_provider_routes_when_get_secret_present() -> None:
    icp = MapPatternToICP().map_with_layer(
        "Gateway", _PY, LayerType.INFRASTRUCTURE,
        ("get_secret", "put_secret"),
        infrastructure_mode="auto",
    )
    assert icp == "python/infrastructure/SecretsProviderICP"


def test_search_routes_when_index_query_present() -> None:
    icp = MapPatternToICP().map_with_layer(
        "Gateway", _PY, LayerType.INFRASTRUCTURE,
        ("index", "query"),
        infrastructure_mode="auto",
    )
    assert icp == "python/infrastructure/SearchICP"


def test_search_routes_when_search_method_present() -> None:
    icp = MapPatternToICP().map_with_layer(
        "Gateway", _PY, LayerType.INFRASTRUCTURE,
        ("search",),
        infrastructure_mode="auto",
    )
    assert icp == "python/infrastructure/SearchICP"


def test_h5b_categories_fall_back_when_manual() -> None:
    icp = MapPatternToICP().map_with_layer(
        "Gateway", _PY, LayerType.INFRASTRUCTURE,
        ("get_secret",),
        infrastructure_mode="manual",
    )
    # Manual mode skips Tier C and falls back to the legacy map(), which
    # routes an abstract Gateway port to the (interface-emitting) GatewayICP.
    assert icp == "python/ddd_clean/GatewayICP"


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
