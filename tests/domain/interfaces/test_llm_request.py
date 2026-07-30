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


def test_cache_key_ignores_seed_and_temperature() -> None:
    # R3.3: seed/temperature never reach the wire, so they must not fragment
    # the cache — identical prompts share a key regardless of these knobs.
    base = LLMRequest(model="m", system_prompt="s", user_prompt="u")
    seeded = LLMRequest(model="m", system_prompt="s", user_prompt="u", seed=1)
    tempy = LLMRequest(
        model="m", system_prompt="s", user_prompt="u", temperature=0.0,
    )
    assert base.cache_key() == seeded.cache_key()
    assert base.cache_key() == tempy.cache_key()


def test_cache_key_still_distinguishes_replicates() -> None:
    base = LLMRequest(model="m", system_prompt="s", user_prompt="u")
    rep = LLMRequest(
        model="m", system_prompt="s", user_prompt="u", replicate_id=1,
    )
    assert base.cache_key() != rep.cache_key()
