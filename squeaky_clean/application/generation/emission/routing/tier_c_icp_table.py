"""tier_c_icp_table: TechSpec category -> Tier C infrastructure ICP name."""

# Patterns whose Infrastructure/Interface-layer instances may route to a
# concrete Tier C adapter ICP instead of their catalog spec
# (see MapPatternToEmitter.map_for).
INFRA_PATTERNS: frozenset[str] = frozenset({"Repository", "Gateway", "Adapter"})

# H1+H3+H5a+H5b heuristic: TechSpec category → Tier C ICP spec name.
# CANONICAL (R6.7): the one category→ICP table; assign_patterns imports it.
CATEGORY_TO_ICP: dict[str, str] = {
    "blob_storage": "BlobStorageAdapterEmitter",
    "kv_cache": "KvCacheEmitter",
    "rest_client": "RestClientEmitter",
    "relational_db": "RelationalDBRepositoryEmitter",
    "document_db": "DocumentDBRepositoryEmitter",
    "message_queue_producer": "MessageQueueProducerEmitter",
    "message_queue_consumer": "MessageQueueConsumerEmitter",
    "stream_processor": "StreamProcessorEmitter",
    "rest_server_handler": "RestServerHandlerEmitter",
    "grpc_client": "GrpcClientEmitter",
    "grpc_server_handler": "GrpcServerHandlerEmitter",
    "websocket_server_handler": "WebSocketServerHandlerEmitter",
    "observability_logger": "ObservabilityLoggerEmitter",
    "secrets_provider": "SecretsProviderEmitter",
    "search": "SearchEmitter",
}

# Inbound-handler categories naturally live in the Interface layer
# (HTTP / RPC / WS endpoints are entry points). All other Tier C
# categories live in the Infrastructure layer.
INTERFACE_LAYER_CATEGORIES: frozenset[str] = frozenset({
    "rest_server_handler",
    "grpc_server_handler",
    "websocket_server_handler",
})
