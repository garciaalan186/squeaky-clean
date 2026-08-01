"""MicroEvalCell DTO: outcome of one pattern x language micro-eval (R5.4)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MicroEvalCell:
    """One compile-verified emission: pattern fixture x target language."""

    # Deliberately `str`, not PatternName: this is the fixture FILE stem
    # (lowercase, e.g. "strategy"), an eval artifact id — not a catalog name.
    pattern: str
    language: str
    passed: bool
    compile_errors: int
    classes_emitted: int
    cost_usd: float
    detail: str = ""
