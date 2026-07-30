"""RegressionAssessment DTO: per-problem gate verdicts + regression records."""

from __future__ import annotations

from dataclasses import dataclass

from squeaky_clean.application.evaluation.eval.report.regression_record import (
    RegressionRecord,
)


@dataclass(frozen=True)
class RegressionAssessment:
    """Outcome of RegressionGate over one sweep: human verdicts + records."""

    verdicts: tuple[str, ...] = ()
    records: tuple[RegressionRecord, ...] = ()

    @property
    def has_regressions(self) -> bool:
        """True when at least one metric tripped the sigma gate."""
        return len(self.records) > 0
