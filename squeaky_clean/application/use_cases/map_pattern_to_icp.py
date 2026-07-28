"""MapPatternToICP: resolve a §Notation PatternName to an ICP spec path."""

from squeaky_clean.application.dtos.language_toolkit import LanguageToolkit
from squeaky_clean.application.use_cases.infrastructure_category_inference import (
    infer_category,
)
from squeaky_clean.domain.value_objects.layer_type import LayerType

# Full GoF + DDD/Clean catalog → category directory under icps/<lang>/.
# Every PatternName in domain.value_objects.pattern_name has a dedicated ICP
# spec in every supported language; test_pattern_icp_resolution enforces that
# invariant against the files on disk. SimpleClassICP is the ONLY fallback and
# is reserved for genuinely unrecognized pattern names — it is never a silent
# stand-in for a catalog pattern that lacks a spec.
_PATTERN_CATEGORY: dict[str, str] = {
    # Creational
    "AbstractFactory": "creational",
    "Builder": "creational",
    "FactoryMethod": "creational",
    "Singleton": "creational",
    "Prototype": "creational",
    # Structural
    "Adapter": "structural",
    "Bridge": "structural",
    "Composite": "structural",
    "Decorator": "structural",
    "Facade": "structural",
    "Flyweight": "structural",
    "Proxy": "structural",
    # Behavioral
    "ChainOfResponsibility": "behavioral",
    "Command": "behavioral",
    "Interpreter": "behavioral",
    "Iterator": "behavioral",
    "Mediator": "behavioral",
    "Memento": "behavioral",
    "Observer": "behavioral",
    "State": "behavioral",
    "Strategy": "behavioral",
    "TemplateMethod": "behavioral",
    "Visitor": "behavioral",
    # DDD / Clean
    "Entity": "ddd_clean",
    "ValueObject": "ddd_clean",
    "Aggregate": "ddd_clean",
    "DomainEvent": "ddd_clean",
    "Specification": "ddd_clean",
    "Repository": "ddd_clean",
    "Gateway": "ddd_clean",
    "Presenter": "ddd_clean",
    "UseCase": "ddd_clean",
    "DTOMapper": "ddd_clean",
    "SimpleClass": "ddd_clean",
}
_FALLBACK_NAME: str = "SimpleClassICP"
_FALLBACK_CATEGORY: str = "ddd_clean"

# Patterns whose Infrastructure/Interface-layer instances may route to a
# concrete Tier C adapter ICP instead of their catalog spec (see map_with_layer).
_INFRA_PATTERNS: frozenset[str] = frozenset({"Repository", "Gateway", "Adapter"})

# H1+H3+H5a+H5b heuristic: TechSpec category → Tier C ICP spec name.
_CATEGORY_TO_ICP: dict[str, str] = {
    "blob_storage": "BlobStorageAdapterICP",
    "kv_cache": "KvCacheICP",
    "rest_client": "RestClientICP",
    "relational_db": "RelationalDBRepositoryICP",
    "document_db": "DocumentDBRepositoryICP",
    "message_queue_producer": "MessageQueueProducerICP",
    "message_queue_consumer": "MessageQueueConsumerICP",
    "stream_processor": "StreamProcessorICP",
    "rest_server_handler": "RestServerHandlerICP",
    "grpc_client": "GrpcClientICP",
    "grpc_server_handler": "GrpcServerHandlerICP",
    "websocket_server_handler": "WebSocketServerHandlerICP",
    "observability_logger": "ObservabilityLoggerICP",
    "secrets_provider": "SecretsProviderICP",
    "search": "SearchICP",
}

# Inbound-handler categories naturally live in the Interface layer
# (HTTP / RPC / WS endpoints are entry points). All other Tier C
# categories live in the Infrastructure layer.
_INTERFACE_LAYER_CATEGORIES: frozenset[str] = frozenset({
    "rest_server_handler",
    "grpc_server_handler",
    "websocket_server_handler",
})


class MapPatternToICP:
    """Maps a pattern name to the slash-qualified ICP spec path to load."""

    def map(self, pattern: str, toolkit: LanguageToolkit) -> str:
        """Return ``<lang>/<category>/<Pattern>ICP`` for any catalog pattern.

        Every recognized GoF/DDD PatternName resolves to its dedicated ICP
        spec. Only a genuinely unrecognized pattern name falls back to
        ``<lang>/ddd_clean/SimpleClassICP``.
        """
        library = toolkit.icp_library
        category = _PATTERN_CATEGORY.get(pattern)
        if category is not None:
            return f"{library}/{category}/{pattern}ICP"
        return f"{library}/{_FALLBACK_CATEGORY}/{_FALLBACK_NAME}"

    def map_with_layer(
        self, pattern: str, toolkit: LanguageToolkit,
        layer: LayerType, method_names: tuple[str, ...] = (),
        infrastructure_mode: str = "manual",
        declared_categories: tuple[str, ...] = (),
    ) -> str:
        """Return Tier C path for Infrastructure Repository/Gateway/Adapter.

        H5a: routes blob_storage/kv_cache/rest_client/relational_db/
        document_db/message_queue_{producer,consumer}/stream_processor when
        ``--infra=auto``. Other inputs fall back to the catalog ``map`` route.

        When ``declared_categories`` is non-empty (passed from the
        ProblemSpec's explicit ``infrastructure_choices``) and the verb
        heuristic returns nothing, fall back to the FIRST declared
        category that has a Tier C ICP — preferring the user's explicit
        choice over silent verb-name guessing.
        """
        if not (
            infrastructure_mode == "auto"
            and pattern in _INFRA_PATTERNS
            and layer in (LayerType.INFRASTRUCTURE, LayerType.INTERFACE)
        ):
            return self.map(pattern, toolkit)
        category = infer_category(method_names)
        if category and not self._layer_matches(category, layer):
            category = None
        icp = _CATEGORY_TO_ICP.get(category) if category else None
        if icp is None and declared_categories:
            for declared in declared_categories:
                if (declared in _CATEGORY_TO_ICP
                        and self._layer_matches(declared, layer)):
                    icp = _CATEGORY_TO_ICP[declared]
                    break
        if icp is not None:
            return f"{toolkit.icp_library}/infrastructure/{icp}"
        return self.map(pattern, toolkit)

    @staticmethod
    def _layer_matches(category: str, layer: LayerType) -> bool:
        """Return True if ``category`` is allowed in ``layer``."""
        if category in _INTERFACE_LAYER_CATEGORIES:
            return layer is LayerType.INTERFACE
        return layer is LayerType.INFRASTRUCTURE
