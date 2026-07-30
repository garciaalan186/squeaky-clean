"""infrastructure_category_inference: derive a TechSpec category from method names."""

from __future__ import annotations

_BLOB_VERBS: frozenset[str] = frozenset({"put_blob", "get_blob", "delete_blob"})
_KV_VERBS: frozenset[str] = frozenset({"set", "get", "expire", "delete"})
_REST_VERBS: frozenset[str] = frozenset({"request", "post", "get", "put"})
_RDB_VERBS: frozenset[str] = frozenset({"save", "find_by_id", "find", "delete"})
_DOC_VERBS: frozenset[str] = frozenset({"upsert", "save", "find_by_id", "find"})
_MQP_VERBS: frozenset[str] = frozenset({"publish", "send"})
_MQC_VERBS: frozenset[str] = frozenset({"consume", "poll", "poll_one", "subscribe"})
_STREAM_VERBS: frozenset[str] = frozenset({"process", "aggregate", "window"})

# H5b verb sets — inbound handlers + observability + secrets + search.
_REST_SRV_VERBS: frozenset[str] = frozenset({"handle", "route", "dispatch"})
_GRPC_CLI_VERBS: frozenset[str] = frozenset({"call", "invoke"})
_GRPC_SRV_VERBS: frozenset[str] = frozenset({"serve", "handle_request"})
_WS_SRV_VERBS: frozenset[str] = frozenset(
    {"accept_connection", "on_message"}
)
_LOG_VERBS: frozenset[str] = frozenset({"info", "warn", "error", "log"})
_SECRETS_VERBS: frozenset[str] = frozenset({"get_secret", "put_secret"})
_SEARCH_VERBS: frozenset[str] = frozenset({"index", "query", "search"})


def _expand(method_names: tuple[str, ...]) -> set[str]:
    """Return each method name plus its bare-verb prefix.

    e.g. ``publish_event`` → {"publish_event", "publish"}. Lets verb-sets
    keyed on bare verbs still match ``<verb>_<noun>`` methods.
    """
    out: set[str] = set()
    for name in method_names:
        low = name.lower()
        out.add(low)
        if "_" in low:
            head, _sep, _tail = low.partition("_")
            out.add(head)
    return out


def infer_category(method_names: tuple[str, ...]) -> str | None:
    """Return the TechSpec category implied by ``method_names`` or ``None``.

    Routing covers H1+H3+H5a+H5b categories. Order matters: more-specific
    verbs run first to disambiguate overlapping signals (e.g. ``get`` vs
    ``get_secret`` vs ``get_blob``). Methods named ``<verb>_<noun>`` are
    matched on their bare ``<verb>`` prefix in addition to the full name
    so the architect can use richer naming (``publish_event``, ``write_blob``)
    without bypassing Tier C routing.
    """
    names = _expand(method_names)
    if "write" in names or "store" in names or "save_blob" in names:
        # write/store on Adapter classes typically means blob storage
        return "blob_storage"
    # Order matters: more-specific verbs first.
    if names & _BLOB_VERBS:
        return "blob_storage"
    if names & _SECRETS_VERBS:
        return "secrets_provider"
    if names & _WS_SRV_VERBS:
        return "websocket_server_handler"
    if names & _GRPC_SRV_VERBS:
        return "grpc_server_handler"
    if names & _MQC_VERBS:
        return "message_queue_consumer"
    if names & _MQP_VERBS:
        return "message_queue_producer"
    if names & _STREAM_VERBS:
        return "stream_processor"
    if "expire" in names or names >= {"set", "get"}:
        return "kv_cache"
    if names & _LOG_VERBS:
        return "observability_logger"
    if names & _SEARCH_VERBS:
        return "search"
    if names & _REST_SRV_VERBS:
        return "rest_server_handler"
    if names & _GRPC_CLI_VERBS:
        return "grpc_client"
    if "request" in names or names >= {"post", "get"}:
        return "rest_client"
    if "upsert" in names:
        return "document_db"
    if names & _RDB_VERBS:
        return "relational_db"
    return None
