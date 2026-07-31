"""ReplayCacheMissError: a replay-only run needed the live API (R5.7)."""

from __future__ import annotations


class ReplayCacheMissError(RuntimeError):
    """Raised when --replay-only hits a prompt absent from the cache.

    Reproducibility contract (R3.3/R5.7): a warm-cache replay is the
    deterministic re-execution mode — identical prompts are served from the
    content-addressed cache at $0. A miss therefore means a prompt/spec
    changed (or the bundle is stale); in CI that is the failure signal.
    """
