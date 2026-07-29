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

    ``max_tokens`` overrides the gateway's default output-token cap for calls
    that emit verbose output (e.g. multi-file Java test skeletons that overflow
    the 4096 default and truncate). It is a capacity knob, not semantic content,
    so it is deliberately EXCLUDED from ``cache_key`` — a fuller response is
    always a valid replacement for a truncated one, and including it would
    fragment the cache on a value that does not change request identity.
    """

    model: str
    system_prompt: str
    user_prompt: str
    temperature: float | None = None
    replicate_id: int = 0
    seed: int | None = None
    tier: str | None = None
    cacheable_user_prefix: str | None = None
    max_tokens: int | None = None

    def cache_key(self) -> str:
        """Stable content-addressed key for caching (model + prompts + replicate).

        ``temperature`` and ``seed`` are deliberately EXCLUDED (R3.3): neither
        gateway forwards them to the wire — the SDK omits them (current models
        deprecate the temperature param and reject seed) and the CLI has no such
        flags — so including them would only fragment the cache, giving a
        ``--deterministic`` (temperature=0.0) run a different key from a default
        (temperature=None) run for a byte-identical request. The warm cache IS
        the reproducibility contract; ``replicate_id`` still distinguishes
        intentionally-repeated samples.
        """
        h = hashlib.sha256()
        h.update(self.model.encode("utf-8"))
        h.update(b"\x00")
        h.update(self.system_prompt.encode("utf-8"))
        h.update(b"\x00")
        h.update(self.user_prompt.encode("utf-8"))
        h.update(b"\x00")
        h.update(str(self.replicate_id).encode("utf-8"))
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
