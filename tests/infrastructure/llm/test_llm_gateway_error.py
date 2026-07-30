"""Tests for LLMGatewayError (R2.6)."""

from squeaky_clean.infrastructure.llm.llm_gateway_error import LLMGatewayError


def test_defaults_to_non_retryable() -> None:
    err = LLMGatewayError("boom")
    assert str(err) == "boom"
    assert err.retryable is False


def test_retryable_flag_is_carried() -> None:
    err = LLMGatewayError("transient", retryable=True)
    assert err.retryable is True


def test_is_a_runtime_error() -> None:
    assert isinstance(LLMGatewayError("x"), RuntimeError)
