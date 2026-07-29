"""E1: ClaudeCLIGateway must degrade gracefully on subprocess timeout."""

import subprocess
from unittest.mock import MagicMock, patch

import pytest

from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.infrastructure.llm.claude_cli_gateway import ClaudeCLIGateway
from squeaky_clean.infrastructure.llm.llm_gateway_error import LLMGatewayError


def _timing_out_proc() -> MagicMock:
    """A fake Popen whose first communicate() times out, second returns."""
    proc = MagicMock()
    proc.pid = 999999999  # non-existent pid → killpg falls back to proc.kill
    proc.returncode = -9
    proc.communicate.side_effect = [
        subprocess.TimeoutExpired(cmd="claude", timeout=1),
        ("", ""),
    ]
    return proc


def test_graceful_timeout_returns_empty_response() -> None:
    gw = ClaudeCLIGateway(graceful_timeout=True, timeout_seconds=1)
    with patch("subprocess.Popen", return_value=_timing_out_proc()):
        out = gw.complete(LLMRequest("m", "sys", "user"))
    assert out.timed_out is True
    assert out.content == ""
    assert out.cost_usd == 0.0


def test_strict_timeout_still_raises() -> None:
    gw = ClaudeCLIGateway(graceful_timeout=False, timeout_seconds=1)
    with patch("subprocess.Popen", return_value=_timing_out_proc()):
        with pytest.raises(LLMGatewayError, match="timed out"):
            gw.complete(LLMRequest("m", "sys", "user"))


def test_strict_timeout_is_retryable() -> None:
    gw = ClaudeCLIGateway(graceful_timeout=False, timeout_seconds=1)
    with patch("subprocess.Popen", return_value=_timing_out_proc()):
        with pytest.raises(LLMGatewayError) as exc_info:
            gw.complete(LLMRequest("m", "sys", "user"))
    assert exc_info.value.retryable is True


def test_spawn_failure_raises_retryable() -> None:
    gw = ClaudeCLIGateway(timeout_seconds=1)
    with patch("subprocess.Popen", side_effect=OSError("no such binary")):
        with pytest.raises(LLMGatewayError) as exc_info:
            gw.complete(LLMRequest("m", "sys", "user"))
    assert exc_info.value.retryable is True


def test_nonzero_exit_with_output_is_not_retryable() -> None:
    proc = MagicMock()
    proc.returncode = 2
    proc.communicate.return_value = ("real diagnostic error", "")
    gw = ClaudeCLIGateway(timeout_seconds=1)
    with patch("subprocess.Popen", return_value=proc):
        with pytest.raises(LLMGatewayError) as exc_info:
            gw.complete(LLMRequest("m", "sys", "user"))
    assert exc_info.value.retryable is False


def test_nonzero_exit_empty_output_is_retryable() -> None:
    proc = MagicMock()
    proc.returncode = 1
    proc.communicate.return_value = ("", "")
    gw = ClaudeCLIGateway(timeout_seconds=1)
    with patch("subprocess.Popen", return_value=proc):
        with pytest.raises(LLMGatewayError) as exc_info:
            gw.complete(LLMRequest("m", "sys", "user"))
    assert exc_info.value.retryable is True
