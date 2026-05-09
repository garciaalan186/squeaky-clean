"""Tests for CLIResponseParser."""

import json

import pytest

from squeaky_clean.infrastructure.llm.cli_response_parser import CLIResponseParser
from squeaky_clean.infrastructure.llm.llm_gateway_error import LLMGatewayError


def test_parse_success_extracts_fields() -> None:
    payload = {
        "type": "result",
        "subtype": "success",
        "is_error": False,
        "duration_ms": 1703,
        "result": "PONG",
        "total_cost_usd": 0.012,
        "usage": {"input_tokens": 10, "output_tokens": 4},
    }
    response = CLIResponseParser().parse(json.dumps(payload))
    assert response.content == "PONG"
    assert response.input_tokens == 10
    assert response.output_tokens == 4
    assert response.cost_usd == pytest.approx(0.012)
    assert response.duration_ms == 1703


def test_parse_error_payload_raises() -> None:
    payload = {"is_error": True, "result": "boom"}
    with pytest.raises(LLMGatewayError):
        CLIResponseParser().parse(json.dumps(payload))


def test_parse_invalid_json_raises() -> None:
    with pytest.raises(LLMGatewayError):
        CLIResponseParser().parse("not json at all")


def test_parse_sums_cache_read_and_creation_tokens() -> None:
    payload = {
        "type": "result",
        "subtype": "success",
        "is_error": False,
        "duration_ms": 1,
        "result": "ok",
        "total_cost_usd": 0.0,
        "usage": {
            "input_tokens": 6,
            "cache_creation_input_tokens": 100,
            "cache_read_input_tokens": 500,
            "output_tokens": 4,
        },
    }
    response = CLIResponseParser().parse(json.dumps(payload))
    assert response.input_tokens == 606  # 6 + 100 + 500
    assert response.output_tokens == 4
