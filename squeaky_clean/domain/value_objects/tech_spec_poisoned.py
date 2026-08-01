"""TechSpecPoisoned: sanitizer-rejection variant of TechSpecResolution (R6.8)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class TechSpecPoisoned:
    """A fetched tech doc was rejected as unsafe by the anti-poisoning gate.

    Distinct from ``TechSpecFetchFailed`` because a poisoned source is a
    security signal (design §4.6), not an availability problem: callers may
    retry a fetch failure but must never retry around the sanitizer.
    """

    reason: str
