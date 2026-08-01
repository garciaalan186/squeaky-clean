"""TechSpecFetchFailed: failure variant of the TechSpecResolution union (R6.8)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class TechSpecFetchFailed:
    """One source failed to produce a TechSpec (fetch/parse/schema error).

    ``reason`` is human-readable and travels to the RunLogger event log and
    into ``TechSpecResolutionError`` — a failed source is never silent.
    """

    reason: str
