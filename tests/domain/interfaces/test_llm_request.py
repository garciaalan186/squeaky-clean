"""Tests for LLMRequest."""

from squeaky_clean.domain.interfaces.llm_request import LLMRequest


def test_llm_request_is_frozen_and_stores_fields() -> None:
    req = LLMRequest(
        model="claude-opus-4-6",
        system_prompt="be concise",
        user_prompt="hello",
    )
    assert req.model == "claude-opus-4-6"
    assert req.system_prompt == "be concise"
    assert req.user_prompt == "hello"
    assert req.seed is None
    assert req.temperature is None


def test_llm_request_seed_field_round_trips() -> None:
    req = LLMRequest(
        model="m", system_prompt="s", user_prompt="u",
        temperature=0.0, seed=42,
    )
    assert req.seed == 42
    assert req.temperature == 0.0


def test_cache_key_changes_with_seed() -> None:
    base = LLMRequest(model="m", system_prompt="s", user_prompt="u")
    seeded = LLMRequest(model="m", system_prompt="s", user_prompt="u", seed=1)
    other_seed = LLMRequest(model="m", system_prompt="s", user_prompt="u", seed=2)
    assert base.cache_key() != seeded.cache_key()
    assert seeded.cache_key() != other_seed.cache_key()
