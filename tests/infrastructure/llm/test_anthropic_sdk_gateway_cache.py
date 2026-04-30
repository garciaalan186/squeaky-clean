"""Unit tests for AnthropicSDKGateway cache_control wiring (no live API)."""

from __future__ import annotations

from typing import cast

import pytest

from squeaky_clean.application.dtos.prompt_cache_config import PromptCacheConfig
from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.infrastructure.llm.anthropic_sdk_gateway import AnthropicSDKGateway


class _FakeUsage:
    input_tokens = 10
    output_tokens = 5
    cache_creation_input_tokens = 0
    cache_read_input_tokens = 0


class _FakeContentBlock:
    def __init__(self, text: str) -> None:
        self.text = text


class _FakeMessage:
    def __init__(self) -> None:
        self.model = "claude-haiku-4-5-20251001"
        self.usage = _FakeUsage()
        self.content = [_FakeContentBlock("ok")]


class _FakeMessages:
    def __init__(self) -> None:
        self.captured: dict[str, object] = {}

    def create(self, **kwargs: object) -> _FakeMessage:
        self.captured = kwargs
        return _FakeMessage()


class _FakeClient:
    def __init__(self) -> None:
        self.messages = _FakeMessages()


def _make_gateway(
    cfg: PromptCacheConfig | None = None,
) -> tuple[AnthropicSDKGateway, _FakeMessages]:
    gw = AnthropicSDKGateway(api_key="sk-test", prompt_cache_config=cfg)
    fake = _FakeClient()
    gw._client = fake  # type: ignore[assignment]
    return gw, fake.messages


def _system(fake: _FakeMessages) -> list[dict[str, object]]:
    return cast("list[dict[str, object]]", fake.captured["system"])


def _messages(fake: _FakeMessages) -> list[dict[str, object]]:
    return cast("list[dict[str, object]]", fake.captured["messages"])


def test_cache_on_attaches_ephemeral_to_system_block() -> None:
    gw, fake = _make_gateway(PromptCacheConfig(enabled=True))
    gw.complete(LLMRequest(
        model="claude-haiku-4-5-20251001",
        system_prompt="SYS", user_prompt="USR", tier="icp",
    ))
    sys_blocks = _system(fake)
    assert sys_blocks[0]["cache_control"] == {"type": "ephemeral"}
    assert sys_blocks[0]["text"] == "SYS"


def test_cache_off_strips_cache_control() -> None:
    gw, fake = _make_gateway(PromptCacheConfig(enabled=False))
    gw.complete(LLMRequest(
        model="claude-haiku-4-5-20251001",
        system_prompt="SYS", user_prompt="USR", tier="icp",
    ))
    sys_blocks = _system(fake)
    assert "cache_control" not in sys_blocks[0]


def test_tier_not_in_allowlist_skips_cache_control() -> None:
    gw, fake = _make_gateway(
        PromptCacheConfig(enabled=True, enabled_tiers=("architect",)),
    )
    gw.complete(LLMRequest(
        model="claude-haiku-4-5-20251001",
        system_prompt="SYS", user_prompt="USR", tier="icp",
    ))
    assert "cache_control" not in _system(fake)[0]


def test_cacheable_user_prefix_adds_two_block_user_message() -> None:
    gw, fake = _make_gateway(PromptCacheConfig(enabled=True))
    gw.complete(LLMRequest(
        model="claude-haiku-4-5-20251001",
        system_prompt="SYS", user_prompt="STABLE_PREFIX dynamic_suffix",
        tier="icp", cacheable_user_prefix="STABLE_PREFIX ",
    ))
    msg = _messages(fake)[0]
    blocks = cast("list[dict[str, object]]", msg["content"])
    assert len(blocks) == 2
    assert blocks[0]["text"] == "STABLE_PREFIX "
    assert blocks[0]["cache_control"] == {"type": "ephemeral"}
    assert blocks[1]["text"] == "dynamic_suffix"
    assert "cache_control" not in blocks[1]


def test_no_prefix_means_plain_string_user_content() -> None:
    gw, fake = _make_gateway(PromptCacheConfig(enabled=True))
    gw.complete(LLMRequest(
        model="claude-haiku-4-5-20251001",
        system_prompt="SYS", user_prompt="USR", tier="icp",
    ))
    msg = _messages(fake)[0]
    assert msg["content"] == "USR"


def test_missing_api_key_raises() -> None:
    import os
    saved = os.environ.pop("ANTHROPIC_API_KEY", None)
    try:
        with pytest.raises(Exception):
            AnthropicSDKGateway()
    finally:
        if saved is not None:
            os.environ["ANTHROPIC_API_KEY"] = saved
