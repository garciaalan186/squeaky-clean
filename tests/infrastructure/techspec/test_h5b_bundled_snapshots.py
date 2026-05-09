"""Schema-validation tests for H5b bundled TechSpec snapshots."""

import json
from pathlib import Path

import pytest

from squeaky_clean.infrastructure.techspec.jsonschema_techspec_validator import (
    JSONSchemaTechSpecValidator,
)

_REPO_ROOT = Path(__file__).resolve().parents[3]
_TECH_ROOT = _REPO_ROOT / "eval" / "tech_specs"
_SCHEMA = _TECH_ROOT / "_schema.v1.json"

_REST_SERVER = [
    "rest_server_handler/flask/Flask==3.0.json",
    "rest_server_handler/fastapi/fastapi==0.110.json",
    "rest_server_handler/starlette/starlette==0.36.json",
]
_GRPC_CLIENT = [
    "grpc_client/grpcio/grpcio==1.62.json",
    "grpc_client/betterproto/betterproto==2.0.json",
]
_GRPC_SERVER = [
    "grpc_server_handler/grpcio/grpcio==1.62.json",
    "grpc_server_handler/betterproto/betterproto==2.0.json",
]
_WEBSOCKET = [
    "websocket_server_handler/websockets/websockets==12.0.json",
    "websocket_server_handler/fastapi/fastapi==0.110.json",
]
_LOGGER = [
    "observability_logger/structlog/structlog==24.1.json",
    "observability_logger/loguru/loguru==0.7.json",
    "observability_logger/stdlib/stdlib.json",
]
_SECRETS = [
    "secrets_provider/aws_secrets_manager/boto3==1.34.json",
    "secrets_provider/azure_key_vault/azure-keyvault-secrets==4.7.json",
    "secrets_provider/env/stdlib.json",
]
_SEARCH = [
    "search/elasticsearch/elasticsearch==8.13.json",
    "search/opensearch/opensearch-py==2.4.json",
]


@pytest.mark.parametrize("relpath", _REST_SERVER)
def test_rest_server_handler_snapshot_validates(relpath: str) -> None:
    spec = json.loads((_TECH_ROOT / relpath).read_text())
    errors = JSONSchemaTechSpecValidator(_SCHEMA).validate(spec)
    assert errors == (), f"{relpath}: {errors}"


@pytest.mark.parametrize("relpath", _GRPC_CLIENT)
def test_grpc_client_snapshot_validates(relpath: str) -> None:
    spec = json.loads((_TECH_ROOT / relpath).read_text())
    errors = JSONSchemaTechSpecValidator(_SCHEMA).validate(spec)
    assert errors == (), f"{relpath}: {errors}"


@pytest.mark.parametrize("relpath", _GRPC_SERVER)
def test_grpc_server_handler_snapshot_validates(relpath: str) -> None:
    spec = json.loads((_TECH_ROOT / relpath).read_text())
    errors = JSONSchemaTechSpecValidator(_SCHEMA).validate(spec)
    assert errors == (), f"{relpath}: {errors}"


@pytest.mark.parametrize("relpath", _WEBSOCKET)
def test_websocket_server_handler_snapshot_validates(relpath: str) -> None:
    spec = json.loads((_TECH_ROOT / relpath).read_text())
    errors = JSONSchemaTechSpecValidator(_SCHEMA).validate(spec)
    assert errors == (), f"{relpath}: {errors}"


@pytest.mark.parametrize("relpath", _LOGGER)
def test_observability_logger_snapshot_validates(relpath: str) -> None:
    spec = json.loads((_TECH_ROOT / relpath).read_text())
    errors = JSONSchemaTechSpecValidator(_SCHEMA).validate(spec)
    assert errors == (), f"{relpath}: {errors}"


@pytest.mark.parametrize("relpath", _SECRETS)
def test_secrets_provider_snapshot_validates(relpath: str) -> None:
    spec = json.loads((_TECH_ROOT / relpath).read_text())
    errors = JSONSchemaTechSpecValidator(_SCHEMA).validate(spec)
    assert errors == (), f"{relpath}: {errors}"


@pytest.mark.parametrize("relpath", _SEARCH)
def test_search_snapshot_validates(relpath: str) -> None:
    spec = json.loads((_TECH_ROOT / relpath).read_text())
    errors = JSONSchemaTechSpecValidator(_SCHEMA).validate(spec)
    assert errors == (), f"{relpath}: {errors}"
