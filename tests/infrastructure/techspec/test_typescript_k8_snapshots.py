"""Schema-validation tests for K8 TypeScript Tier C TechSpec snapshots."""

import json
from pathlib import Path

import pytest

from squeaky_clean.infrastructure.techspec.jsonschema_techspec_validator import (
    JSONSchemaTechSpecValidator,
)

_REPO_ROOT = Path(__file__).resolve().parents[3]
_TECH_ROOT = _REPO_ROOT / "eval" / "tech_specs"
_SCHEMA = _TECH_ROOT / "_schema.v1.json"

_K8_TS_SNAPSHOTS = [
    "blob_storage/aws_s3_ts/@aws-sdk--client-s3==3.600.json",
    "blob_storage/local_disk/node-fs-ts.json",
    "kv_cache/ioredis_ts/ioredis==5.3.json",
    "kv_cache/redis_node_ts/redis==4.6.json",
    "rest_client/axios_ts/axios==1.6.json",
    "rest_client/undici_ts/undici==6.6.json",
    "relational_db/pg_ts/pg==8.11.json",
    "relational_db/sqlite_ts/better-sqlite3==9.4.json",
    "document_db/mongodb_ts/mongodb==6.3.json",
    "document_db/dynamodb_ts/@aws-sdk--client-dynamodb==3.600.json",
    "message_queue_producer/kafkajs_ts/kafkajs==2.2.json",
    "message_queue_producer/sqs_ts/@aws-sdk--client-sqs==3.600.json",
    "message_queue_consumer/kafkajs_ts/kafkajs==2.2.json",
    "message_queue_consumer/sqs_ts/@aws-sdk--client-sqs==3.600.json",
    "stream_processor/kafkajs_stream_ts/kafkajs==2.2.json",
    "stream_processor/kinesis_ts/@aws-sdk--client-kinesis==3.600.json",
    "rest_server_handler/express_ts/express==4.19.json",
    "rest_server_handler/fastify_ts/fastify==4.26.json",
    "grpc_client/grpc_js_ts/@grpc--grpc-js==1.10.json",
    "grpc_client/connect_ts/@connectrpc--connect==1.4.json",
    "grpc_server_handler/grpc_js_ts/@grpc--grpc-js==1.10.json",
    "grpc_server_handler/connect_ts/@connectrpc--connect==1.4.json",
    "websocket_server_handler/ws_ts/ws==8.16.json",
    "websocket_server_handler/socketio_ts/socket.io==4.7.json",
    "observability_logger/winston_ts/winston==3.11.json",
    "observability_logger/pino_ts/pino==8.19.json",
    "secrets_provider/aws_secrets_ts/@aws-sdk--client-secrets-manager==3.600.json",
    "secrets_provider/env_only_ts/stdlib-node-ts.json",
    "search/elasticsearch_ts/@elastic--elasticsearch==8.13.json",
    "search/opensearch_ts/@opensearch-project--opensearch==2.6.json",
]


@pytest.mark.parametrize("relpath", _K8_TS_SNAPSHOTS)
def test_k8_ts_snapshot_validates(relpath: str) -> None:
    spec = json.loads((_TECH_ROOT / relpath).read_text())
    errors = JSONSchemaTechSpecValidator(_SCHEMA).validate(spec)
    assert errors == (), f"{relpath}: {errors}"


@pytest.mark.parametrize("relpath", _K8_TS_SNAPSHOTS)
def test_k8_ts_snapshot_language_is_typescript(relpath: str) -> None:
    spec = json.loads((_TECH_ROOT / relpath).read_text())
    assert spec["language"] == "typescript"


@pytest.mark.parametrize("relpath", _K8_TS_SNAPSHOTS)
def test_k8_ts_snapshot_uses_npm(relpath: str) -> None:
    spec = json.loads((_TECH_ROOT / relpath).read_text())
    assert spec["install"]["manager"] in ("npm", "stdlib")


def test_k8_ts_covers_at_least_two_per_category() -> None:
    counts: dict[str, int] = {}
    for rel in _K8_TS_SNAPSHOTS:
        cat = rel.split("/", 1)[0]
        counts[cat] = counts.get(cat, 0) + 1
    for cat, n in counts.items():
        assert n >= 2, f"{cat} has only {n} snapshot(s); need >=2"
    assert len(counts) == 15, f"expected 15 distinct categories, got {len(counts)}"
