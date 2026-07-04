"""PatternScorer: merge per-layer fingerprint scorers into one score map."""

from squeaky_clean.application.dtos.recovery.class_record import ClassRecord
from squeaky_clean.application.use_cases.recovery.domain_pattern_scorer import (
    DomainPatternScorer,
)
from squeaky_clean.application.use_cases.recovery.infra_pattern_scorer import (
    InfraPatternScorer,
)
from squeaky_clean.application.use_cases.recovery.orchestration_pattern_scorer import (
    OrchestrationPatternScorer,
)
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.pattern_name import PatternName


class PatternScorer:
    """Deterministic pattern fingerprinting across all layer scorers.

    Delegates to the domain, infrastructure, and orchestration scorers and
    unions their candidate scores. The result feeds PatternClassifier,
    which picks the top score or escalates a tie. No LLM participates —
    the same class always yields the same score map.
    """

    def __init__(self) -> None:
        self._scorers = (
            DomainPatternScorer(), InfraPatternScorer(), OrchestrationPatternScorer(),
        )

    def score(self, record: ClassRecord, layer: LayerType) -> dict[PatternName, int]:
        """Return the merged candidate-pattern score map for one class."""
        out: dict[PatternName, int] = {}
        for scorer in self._scorers:
            out.update(scorer.score(record, layer))
        return out
