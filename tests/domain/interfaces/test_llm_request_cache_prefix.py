"""Tests for LLMRequest.cacheable_prefix_hash determinism."""

from squeaky_clean.domain.interfaces.llm_request import LLMRequest


def test_prefix_hash_equal_across_runs_same_inputs() -> None:
    a = LLMRequest(
        model="claude-haiku-4-5-20251001",
        system_prompt="ICP system spec body",
        user_prompt="ASSIGNMENT 1 details ...",
        tier="icp",
        cacheable_user_prefix="SIBLING_INTERFACES section",
    )
    b = LLMRequest(
        model="claude-haiku-4-5-20251001",
        system_prompt="ICP system spec body",
        user_prompt="ASSIGNMENT 2 details ...",
        tier="icp",
        cacheable_user_prefix="SIBLING_INTERFACES section",
    )
    assert a.cacheable_prefix_hash() == b.cacheable_prefix_hash()


def test_prefix_hash_excludes_replicate_id_and_seed() -> None:
    a = LLMRequest(
        model="m", system_prompt="s", user_prompt="u",
        tier="icp", cacheable_user_prefix="p",
        replicate_id=0, seed=0,
    )
    b = LLMRequest(
        model="m", system_prompt="s", user_prompt="u-different",
        tier="icp", cacheable_user_prefix="p",
        replicate_id=99, seed=12345,
    )
    assert a.cacheable_prefix_hash() == b.cacheable_prefix_hash()


def test_prefix_hash_changes_when_system_prompt_changes() -> None:
    a = LLMRequest(model="m", system_prompt="s1", user_prompt="u", tier="icp")
    b = LLMRequest(model="m", system_prompt="s2", user_prompt="u", tier="icp")
    assert a.cacheable_prefix_hash() != b.cacheable_prefix_hash()


def test_prefix_hash_changes_when_tier_changes() -> None:
    a = LLMRequest(model="m", system_prompt="s", user_prompt="u", tier="icp")
    b = LLMRequest(
        model="m", system_prompt="s", user_prompt="u", tier="architect",
    )
    assert a.cacheable_prefix_hash() != b.cacheable_prefix_hash()
