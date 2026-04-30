"""InfrastructureCategory: enumerated TechSpec category names (H1)."""

from typing import Literal, get_args

InfrastructureCategory = Literal[
    "blob_storage",
    "relational_db",
    "document_db",
    "kv_cache",
    "message_queue_producer",
    "message_queue_consumer",
    "stream_processor",
    "rest_client",
    "rest_server_handler",
    "grpc_client",
    "grpc_server_handler",
    "websocket_server_handler",
    "observability_logger",
    "secrets_provider",
    "search",
]

ALL_INFRASTRUCTURE_CATEGORIES: frozenset[str] = frozenset(
    get_args(InfrastructureCategory)
)
