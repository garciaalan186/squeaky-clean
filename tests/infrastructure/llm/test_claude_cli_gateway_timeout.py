"""E1: ClaudeCLIGateway must degrade gracefully on subprocess timeout."""

import subprocess
from unittest.mock import patch

import pytest

from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.infrastructure.llm.claude_cli_gateway import ClaudeCLIGateway
from squeaky_clean.infrastructure.llm.llm_gateway_error import LLMGatewayError


def _raise_timeout(*_args: object, **_kwargs: object) -> None:
    raise subprocess.TimeoutExpired(cmd="claude", timeout=180)


def test_graceful_timeout_returns_empty_response() -> None:
    gw = ClaudeCLIGateway(graceful_timeout=True, timeout_seconds=1)
    with patch("subprocess.run", side_effect=_raise_timeout):
        out = gw.complete(LLMRequest("m", "sys", "user"))
    assert out.timed_out is True
    assert out.content == ""
    assert out.cost_usd == 0.0


def test_strict_timeout_still_raises() -> None:
    gw = ClaudeCLIGateway(graceful_timeout=False, timeout_seconds=1)
    with patch("subprocess.run", side_effect=_raise_timeout):
        with pytest.raises(LLMGatewayError, match="timed out"):
            gw.complete(LLMRequest("m", "sys", "user"))
