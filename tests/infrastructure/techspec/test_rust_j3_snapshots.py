"""Schema-validation tests for J3 Rust Tier C TechSpec snapshots."""

import json
from pathlib import Path

import pytest

from squeaky_clean.infrastructure.techspec.jsonschema_techspec_validator import (
    JSONSchemaTechSpecValidator,
)

_REPO_ROOT = Path(__file__).resolve().parents[3]
_TECH_ROOT = _REPO_ROOT / "eval" / "tech_specs"
_SCHEMA = _TECH_ROOT / "_schema.v1.json"

_J3_SNAPSHOTS = [
    "blob_storage/aws_s3_rust/aws-sdk-s3==1.40.json",
    "blob_storage/local_disk/stdlib-rust.json",
    "kv_cache/redis_rust/redis==0.25.json",
    "kv_cache/memcache_rust/memcache==0.17.json",
    "rest_client/reqwest/reqwest==0.12.json",
    "rest_client/hyper/hyper==1.2.json",
    "relational_db/sqlx_pg/sqlx==0.7.json",
    "relational_db/tokio_postgres/tokio-postgres==0.7.json",
    "document_db/mongodb_rust/mongodb==2.8.json",
    "document_db/dynamodb_rust/aws-sdk-dynamodb==1.31.json",
    "message_queue_producer/rdkafka/rdkafka==0.36.json",
    "message_queue_producer/kafka_rs/kafka==0.10.json",
    "message_queue_consumer/rdkafka/rdkafka==0.36.json",
    "message_queue_consumer/kafka_rs/kafka==0.10.json",
    "stream_processor/rdkafka_consumer_group/rdkafka==0.36.json",
    "stream_processor/kafka_rs/kafka==0.10.json",
    "rest_server_handler/axum/axum==0.7.json",
    "rest_server_handler/actix_web/actix-web==4.5.json",
    "rest_server_handler/warp/warp==0.3.json",
    "grpc_client/tonic/tonic==0.11.json",
    "grpc_client/grpcio_rust/grpcio==0.13.json",
    "grpc_server_handler/tonic/tonic==0.11.json",
    "grpc_server_handler/grpcio_rust/grpcio==0.13.json",
    "websocket_server_handler/tokio_tungstenite/tokio-tungstenite==0.21.json",
    "websocket_server_handler/axum_ws/axum==0.7.json",
    "observability_logger/tracing/tracing==0.1.json",
    "observability_logger/log4rs/log4rs==1.3.json",
    "secrets_provider/aws_secrets_manager_rust/aws-sdk-secretsmanager==1.30.json",
    "secrets_provider/dotenv_only/dotenv==0.15.json",
    "search/elasticsearch_rust/elasticsearch==8.5.json",
    "search/meilisearch_rust/meilisearch-sdk==0.27.json",
]


@pytest.mark.parametrize("relpath", _J3_SNAPSHOTS)
def test_j3_snapshot_validates(relpath: str) -> None:
    spec = json.loads((_TECH_ROOT / relpath).read_text())
    errors = JSONSchemaTechSpecValidator(_SCHEMA).validate(spec)
    assert errors == (), f"{relpath}: {errors}"


@pytest.mark.parametrize("relpath", _J3_SNAPSHOTS)
def test_j3_snapshot_language_is_rust(relpath: str) -> None:
    spec = json.loads((_TECH_ROOT / relpath).read_text())
    assert spec["language"] == "rust"


@pytest.mark.parametrize("relpath", _J3_SNAPSHOTS)
def test_j3_snapshot_uses_cargo_or_stdlib(relpath: str) -> None:
    spec = json.loads((_TECH_ROOT / relpath).read_text())
    assert spec["install"]["manager"] in ("cargo", "stdlib")


def test_j3_covers_at_least_two_per_category() -> None:
    counts: dict[str, int] = {}
    for rel in _J3_SNAPSHOTS:
        cat = rel.split("/", 1)[0]
        counts[cat] = counts.get(cat, 0) + 1
    for cat, n in counts.items():
        assert n >= 2, f"{cat} has only {n} snapshot(s); need >=2"
    assert len(counts) == 15, f"expected 15 distinct categories, got {len(counts)}"
