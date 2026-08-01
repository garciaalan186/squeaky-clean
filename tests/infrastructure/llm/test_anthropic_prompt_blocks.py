"""Unit tests for AnthropicPromptBlocks (extracted from the SDK gateway)."""

from __future__ import annotations

from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.infrastructure.llm.anthropic_prompt_blocks import AnthropicPromptBlocks


def _request(user: str = "USR", prefix: str | None = None) -> LLMRequest:
    return LLMRequest(
        model="claude-haiku-4-5-20251001",
        system_prompt="SYS", user_prompt=user,
        cacheable_user_prefix=prefix,
    )


def test_system_block_gets_cache_control_when_cache_on() -> None:
    blocks = AnthropicPromptBlocks().build_system(_request(), True)
    assert blocks == [{
        "type": "text", "text": "SYS",
        "cache_control": {"type": "ephemeral"},
    }]


def test_system_block_plain_when_cache_off() -> None:
    blocks = AnthropicPromptBlocks().build_system(_request(), False)
    assert blocks == [{"type": "text", "text": "SYS"}]


def test_messages_are_plain_string_without_prefix() -> None:
    msgs = AnthropicPromptBlocks().build_messages(_request(), True)
    assert msgs == [{"role": "user", "content": "USR"}]


def test_cacheable_prefix_becomes_ephemeral_block_plus_suffix() -> None:
    msgs = AnthropicPromptBlocks().build_messages(
        _request(user="PREFIX-SUFFIX", prefix="PREFIX-"), True,
    )
    content = msgs[0]["content"]
    assert isinstance(content, list)
    assert content[0] == {
        "type": "text", "text": "PREFIX-",
        "cache_control": {"type": "ephemeral"},
    }
    assert content[1] == {"type": "text", "text": "SUFFIX"}


def test_non_matching_prefix_keeps_full_prompt_as_suffix() -> None:
    msgs = AnthropicPromptBlocks().build_messages(
        _request(user="BODY", prefix="OTHER-"), True,
    )
    content = msgs[0]["content"]
    assert isinstance(content, list)
    assert content[1] == {"type": "text", "text": "BODY"}
