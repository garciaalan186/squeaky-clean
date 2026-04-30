"""Schema-validation tests for J2 Go Tier C TechSpec snapshots."""

import json
from pathlib import Path

import pytest

from squeaky_clean.infrastructure.techspec.jsonschema_techspec_validator import (
    JSONSchemaTechSpecValidator,
)

_REPO_ROOT = Path(__file__).resolve().parents[3]
_TECH_ROOT = _REPO_ROOT / "eval" / "tech_specs"
_SCHEMA = _TECH_ROOT / "_schema.v1.json"

_J2_SNAPSHOTS = [
    "blob_storage/aws_s3_go/aws-sdk-go-v2-s3==1.66.json",
    "blob_storage/local_disk/stdlib-go.json",
    "kv_cache/go_redis/go-redis-v9==9.5.json",
    "kv_cache/memcache/gomemcache==1.0.json",
    "rest_client/stdlib_http/stdlib-go.json",
    "rest_client/resty/resty==2.11.json",
    "relational_db/postgres_pq/lib_pq==1.10.json",
    "relational_db/sqlite_modernc/modernc-sqlite==1.29.json",
    "document_db/mongo_driver/mongo-go-driver==1.13.json",
    "document_db/dynamodb_go/aws-sdk-go-v2-dynamodb==1.30.json",
    "message_queue_producer/confluent_kafka_go/confluent-kafka-go==2.3.json",
    "message_queue_producer/sarama/Shopify-sarama==1.42.json",
    "message_queue_consumer/confluent_kafka_go/confluent-kafka-go==2.3.json",
    "message_queue_consumer/sarama/Shopify-sarama==1.42.json",
    "stream_processor/sarama_consumer_group/Shopify-sarama==1.42.json",
    "stream_processor/kafka_go/segmentio-kafka-go==0.4.json",
    "rest_server_handler/gorilla_mux/gorilla-mux==1.8.json",
    "rest_server_handler/gin/gin==1.9.json",
    "rest_server_handler/stdlib_http/stdlib-go.json",
    "grpc_client/grpc_go/google.golang.org-grpc==1.62.json",
    "grpc_client/connect_go/connect-go==1.16.json",
    "grpc_server_handler/grpc_go/google.golang.org-grpc==1.62.json",
    "grpc_server_handler/connect_go/connect-go==1.16.json",
    "websocket_server_handler/gorilla_websocket/gorilla-websocket==1.5.json",
    "websocket_server_handler/nhooyr_websocket/nhooyr-websocket==1.8.json",
    "observability_logger/zap/uber-zap==1.26.json",
    "observability_logger/slog/stdlib-go.json",
    "secrets_provider/aws_secrets_manager_go/aws-sdk-go-v2-secretsmanager==1.30.json",
    "secrets_provider/env_only/stdlib-go.json",
    "search/elasticsearch_go/go-elasticsearch-v8==8.13.json",
    "search/opensearch_go/opensearch-go==2.3.json",
]


@pytest.mark.parametrize("relpath", _J2_SNAPSHOTS)
def test_j2_snapshot_validates(relpath: str) -> None:
    spec = json.loads((_TECH_ROOT / relpath).read_text())
    errors = JSONSchemaTechSpecValidator(_SCHEMA).validate(spec)
    assert errors == (), f"{relpath}: {errors}"


@pytest.mark.parametrize("relpath", _J2_SNAPSHOTS)
def test_j2_snapshot_language_is_go(relpath: str) -> None:
    spec = json.loads((_TECH_ROOT / relpath).read_text())
    assert spec["language"] == "go"


@pytest.mark.parametrize("relpath", _J2_SNAPSHOTS)
def test_j2_snapshot_uses_go_or_stdlib(relpath: str) -> None:
    spec = json.loads((_TECH_ROOT / relpath).read_text())
    assert spec["install"]["manager"] in ("go", "stdlib")


def test_j2_covers_at_least_two_per_category() -> None:
    counts: dict[str, int] = {}
    for rel in _J2_SNAPSHOTS:
        cat = rel.split("/", 1)[0]
        counts[cat] = counts.get(cat, 0) + 1
    for cat, n in counts.items():
        assert n >= 2, f"{cat} has only {n} snapshot(s); need >=2"
    assert len(counts) == 15, f"expected 15 distinct categories, got {len(counts)}"
