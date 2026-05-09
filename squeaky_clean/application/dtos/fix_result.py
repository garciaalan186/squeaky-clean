"""FixResult DTO: aggregated outcome of a fixer-stage dispatch."""

from dataclasses import dataclass

from squeaky_clean.application.dtos.implemented_class import ImplementedClass


@dataclass(frozen=True)
class FixResult:
    """Aggregated stats + rewritten classes from one fixer-stage run.

    `fixed_classes` holds the updated ImplementedClass instances that
    the caller should re-integrate to disk. Token/cost/duration fields
    let the metrics builder bucket fixer usage separately from ICP.
    """

    fixed_classes: tuple[ImplementedClass, ...]
    input_tokens: int
    output_tokens: int
    cost_usd: float
    duration_ms: int
