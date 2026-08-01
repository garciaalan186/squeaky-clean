"""AnthropicPromptBlocks: system/user block construction with cache_control."""

from __future__ import annotations

from anthropic.types import MessageParam, TextBlockParam

from squeaky_clean.domain.interfaces.llm_request import LLMRequest


class AnthropicPromptBlocks:
    """Builds the SDK message blocks, attaching ephemeral cache markers."""

    def build_system(
        self, request: LLMRequest, cache_on: bool,
    ) -> list[TextBlockParam]:
        """One system block; cache_control added when caching is enabled."""
        if cache_on:
            block: TextBlockParam = {
                "type": "text", "text": request.system_prompt,
                "cache_control": {"type": "ephemeral"},
            }
        else:
            block = {"type": "text", "text": request.system_prompt}
        return [block]

    def build_messages(
        self, request: LLMRequest, cache_on: bool,
    ) -> list[MessageParam]:
        """User message; a cacheable prefix becomes its own ephemeral block."""
        prefix = request.cacheable_user_prefix
        if not cache_on or not prefix:
            return [{"role": "user", "content": request.user_prompt}]
        suffix = request.user_prompt[len(prefix):] if (
            request.user_prompt.startswith(prefix)
        ) else request.user_prompt
        prefix_block: TextBlockParam = {
            "type": "text", "text": prefix,
            "cache_control": {"type": "ephemeral"},
        }
        suffix_block: TextBlockParam = {"type": "text", "text": suffix}
        return [{"role": "user", "content": [prefix_block, suffix_block]}]
