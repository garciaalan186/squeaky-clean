"""AgentScore DTO: per-agent unit-eval result."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AgentScore:
    """Pass/fail signal for one agent invocation against frozen criteria."""

    agent: str
    fixture: str
    parsed: bool
    structural_pass: float
    issues: tuple[str, ...]
