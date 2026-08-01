"""PromptCandidate DTO: one prompt variant + its mean score on a fixture set."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PromptCandidate:
    """One prompt variant evaluated against fixtures."""

    name: str
    system_prompt: str
    mean_score: float
    fixtures_passed: int
    fixtures_total: int
