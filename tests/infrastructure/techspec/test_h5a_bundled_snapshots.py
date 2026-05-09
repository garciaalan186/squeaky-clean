"""Schema-validation tests for H5a bundled TechSpec snapshots."""

import json
from pathlib import Path

import pytest

from squeaky_clean.infrastructure.techspec.jsonschema_techspec_validator import (
    JSONSchemaTechSpecValidator,
)

_REPO_ROOT = Path(__file__).resolve().parents[3]
_TECH_ROOT = _REPO_ROOT / "eval" / "tech_specs"
_SCHEMA = _TECH_ROOT / "_schema.v1.json"

_RELATIONAL_DB = [
    "relational_db/sqlite/stdlib.json",
    "relational_db/postgres/psycopg2==2.9.json",
    "relational_db/mysql/PyMySQL==1.1.json",
]
_DOCUMENT_DB = [
    "document_db/mongodb/pymongo==4.6.json",
    "document_db/dynamodb/boto3==1.34.json",
    "document_db/cosmos/azure-cosmos==4.5.json",
]
_MQ_PRODUCER = [
    "message_queue_producer/kafka/confluent-kafka==2.5.json",
    "message_queue_producer/rabbitmq/pika==1.3.json",
    "message_queue_producer/sqs/boto3==1.34.json",
]
_MQ_CONSUMER = [
    "message_queue_consumer/kafka/confluent-kafka==2.5.json",
    "message_queue_consumer/rabbitmq/pika==1.3.json",
    "message_queue_consumer/sqs/boto3==1.34.json",
]
_STREAM = [
    "stream_processor/kafka_streams/confluent-kafka==2.5.json",
    "stream_processor/flink/apache-flink==1.18.json",
    "stream_processor/beam/apache-beam==2.55.json",
]


@pytest.mark.parametrize("relpath", _RELATIONAL_DB)
def test_relational_db_snapshot_validates(relpath: str) -> None:
    spec = json.loads((_TECH_ROOT / relpath).read_text())
    errors = JSONSchemaTechSpecValidator(_SCHEMA).validate(spec)
    assert errors == (), f"{relpath}: {errors}"


@pytest.mark.parametrize("relpath", _DOCUMENT_DB)
def test_document_db_snapshot_validates(relpath: str) -> None:
    spec = json.loads((_TECH_ROOT / relpath).read_text())
    errors = JSONSchemaTechSpecValidator(_SCHEMA).validate(spec)
    assert errors == (), f"{relpath}: {errors}"


@pytest.mark.parametrize("relpath", _MQ_PRODUCER)
def test_mq_producer_snapshot_validates(relpath: str) -> None:
    spec = json.loads((_TECH_ROOT / relpath).read_text())
    errors = JSONSchemaTechSpecValidator(_SCHEMA).validate(spec)
    assert errors == (), f"{relpath}: {errors}"


@pytest.mark.parametrize("relpath", _MQ_CONSUMER)
def test_mq_consumer_snapshot_validates(relpath: str) -> None:
    spec = json.loads((_TECH_ROOT / relpath).read_text())
    errors = JSONSchemaTechSpecValidator(_SCHEMA).validate(spec)
    assert errors == (), f"{relpath}: {errors}"


@pytest.mark.parametrize("relpath", _STREAM)
def test_stream_processor_snapshot_validates(relpath: str) -> None:
    spec = json.loads((_TECH_ROOT / relpath).read_text())
    errors = JSONSchemaTechSpecValidator(_SCHEMA).validate(spec)
    assert errors == (), f"{relpath}: {errors}"
