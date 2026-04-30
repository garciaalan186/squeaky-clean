"""EvalResult DTO: the output of one RunEval.execute() invocation."""

from dataclasses import dataclass
from pathlib import Path

from squeaky_clean.application.dtos.eval_metrics import EvalMetrics


@dataclass(frozen=True)
class EvalResult:
    """Immutable bundle of a problem id, its metrics, and its report path."""

    problem_id: str
    metrics: EvalMetrics
    report_path: Path
