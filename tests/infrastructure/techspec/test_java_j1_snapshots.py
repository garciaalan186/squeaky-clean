"""Schema-validation tests for J1 Java Tier C TechSpec snapshots."""

import json
from pathlib import Path

import pytest

from squeaky_clean.infrastructure.techspec.jsonschema_techspec_validator import (
    JSONSchemaTechSpecValidator,
)

_REPO_ROOT = Path(__file__).resolve().parents[3]
_TECH_ROOT = _REPO_ROOT / "eval" / "tech_specs"
_SCHEMA = _TECH_ROOT / "_schema.v1.json"

_J1_SNAPSHOTS = [
    "relational_db/spring_data_jdbc/spring-boot-starter-data-jdbc==2.7.json",
    "relational_db/jdbi/jdbi3-core==3.45.json",
    "document_db/spring_data_mongodb/spring-boot-starter-data-mongodb==2.7.json",
    "document_db/dynamodb_enhanced/aws-sdk-java-v2==2.25.json",
    "kv_cache/spring_data_redis/spring-boot-starter-data-redis==2.7.json",
    "kv_cache/lettuce/lettuce-core==6.3.json",
    "rest_client/spring_rest_client/spring-web==5.3.json",
    "rest_client/okhttp/okhttp==4.12.json",
    "grpc_client/grpc_java/grpc-netty-shaded==1.62.json",
    "grpc_client/grpc_java/grpc-okhttp==1.62.json",
    "grpc_server_handler/grpc_java/grpc-netty-shaded==1.62.json",
    "grpc_server_handler/grpc_spring_boot/grpc-server-spring-boot-starter==2.15.json",
    "websocket_server_handler/spring_websocket/spring-boot-starter-websocket==2.7.json",
    "websocket_server_handler/jakarta_ws/jakarta.websocket-api==2.1.json",
    "observability_logger/slf4j_logback/logback-classic==1.2.json",
    "observability_logger/log4j2/log4j-core==2.22.json",
    "secrets_provider/aws_secrets_manager/aws-sdk-java-v2==2.25.json",
    "secrets_provider/spring_cloud_config/spring-cloud-starter-config==3.1.json",
    "search/spring_data_elasticsearch/spring-boot-starter-data-elasticsearch==2.7.json",
    "search/elasticsearch_java/elasticsearch-java==8.13.json",
    "stream_processor/kafka_streams/kafka-streams==3.6.json",
    "stream_processor/spring_cloud_stream/spring-cloud-stream-binder-kafka-streams==4.0.json",
]


@pytest.mark.parametrize("relpath", _J1_SNAPSHOTS)
def test_j1_snapshot_validates(relpath: str) -> None:
    spec = json.loads((_TECH_ROOT / relpath).read_text())
    errors = JSONSchemaTechSpecValidator(_SCHEMA).validate(spec)
    assert errors == (), f"{relpath}: {errors}"


@pytest.mark.parametrize("relpath", _J1_SNAPSHOTS)
def test_j1_snapshot_language_is_java(relpath: str) -> None:
    spec = json.loads((_TECH_ROOT / relpath).read_text())
    assert spec["language"] == "java"


@pytest.mark.parametrize("relpath", _J1_SNAPSHOTS)
def test_j1_snapshot_uses_maven(relpath: str) -> None:
    spec = json.loads((_TECH_ROOT / relpath).read_text())
    assert spec["install"]["manager"] == "maven"
