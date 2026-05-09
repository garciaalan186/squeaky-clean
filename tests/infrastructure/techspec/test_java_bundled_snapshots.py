"""Schema-validation tests for Java-language bundled TechSpec snapshots."""

import json
from pathlib import Path

import pytest

from squeaky_clean.infrastructure.techspec.jsonschema_techspec_validator import (
    JSONSchemaTechSpecValidator,
)

_REPO_ROOT = Path(__file__).resolve().parents[3]
_TECH_ROOT = _REPO_ROOT / "eval" / "tech_specs"
_SCHEMA = _TECH_ROOT / "_schema.v1.json"

_JAVA_SNAPSHOTS = [
    "rest_server_handler/spring_boot/spring-boot-starter-web==3.2.json",
    "message_queue_producer/spring_kafka/spring-kafka==3.1.json",
    "message_queue_consumer/spring_kafka/spring-kafka==3.1.json",
    "blob_storage/local_disk/jdk.json",
    "blob_storage/s3/aws-sdk-java-v2==2.25.json",
]


@pytest.mark.parametrize("relpath", _JAVA_SNAPSHOTS)
def test_java_snapshot_validates(relpath: str) -> None:
    spec = json.loads((_TECH_ROOT / relpath).read_text())
    errors = JSONSchemaTechSpecValidator(_SCHEMA).validate(spec)
    assert errors == (), f"{relpath}: {errors}"


@pytest.mark.parametrize("relpath", _JAVA_SNAPSHOTS)
def test_java_snapshot_language_field(relpath: str) -> None:
    spec = json.loads((_TECH_ROOT / relpath).read_text())
    assert spec["language"] == "java", f"{relpath} not language=java"
