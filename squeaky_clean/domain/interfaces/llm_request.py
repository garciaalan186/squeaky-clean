"""LLMRequest DTO: a single prompt submitted to an LLMGateway."""

import hashlib
from dataclasses import dataclass


@dataclass(frozen=True)
class LLMRequest:
    """Immutable request bundling model selection and prompts.

    ``tier`` is an optional label ({"architect","manager","icp","fixer"})
    propagated from the use case so adapters (e.g. AnthropicSDKGateway)
    can decide whether to attach Anthropic ``cache_control`` blocks.
    It is not part of ``cache_key`` because the model already determines
    the tier in the canonical routing.
    """

    model: str
    system_prompt: str
    user_prompt: str
    temperature: float | None = None
    replicate_id: int = 0
    seed: int | None = None
    tier: str | None = None
    cacheable_user_prefix: str | None = None

    def cache_key(self) -> str:
        """Stable content-addressed key for caching (model+prompts+sampling)."""
        h = hashlib.sha256()
        h.update(self.model.encode("utf-8"))
        h.update(b"\x00")
        h.update(self.system_prompt.encode("utf-8"))
        h.update(b"\x00")
        h.update(self.user_prompt.encode("utf-8"))
        h.update(b"\x00")
        temp_str = "" if self.temperature is None else f"{self.temperature:.4f}"
        h.update(temp_str.encode("utf-8"))
        h.update(b"\x00")
        h.update(str(self.replicate_id).encode("utf-8"))
        h.update(b"\x00")
        seed_str = "" if self.seed is None else str(self.seed)
        h.update(seed_str.encode("utf-8"))
        return h.hexdigest()

    def cacheable_prefix_hash(self) -> str:
        """SHA-256 of the cacheable prefix (model + system + tier).

        This deliberately excludes timestamps, run/replicate ids, seeds,
        and the dynamic user suffix — it is the portion that determines
        whether two calls share a cache breakpoint.
        """
        h = hashlib.sha256()
        h.update(self.model.encode("utf-8"))
        h.update(b"\x00")
        h.update(self.system_prompt.encode("utf-8"))
        h.update(b"\x00")
        h.update((self.tier or "").encode("utf-8"))
        h.update(b"\x00")
        h.update((self.cacheable_user_prefix or "").encode("utf-8"))
        return h.hexdigest()
