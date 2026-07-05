"""PatternClassifier: assign each class its GoF/DDD pattern (Stage 3)."""

from squeaky_clean.application.dtos.recovery.class_catalog import ClassCatalog
from squeaky_clean.application.use_cases.recovery.pattern_scorer import PatternScorer
from squeaky_clean.application.use_cases.recovery.pattern_tiebreak import PatternTiebreak
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.pattern_name import PatternName


class PatternClassifier:
    """Classifies each class against the 34-pattern catalog.

    Deterministic fingerprints score the candidates; a unique top score
    wins outright. A two-or-more-way tie escalates to the injected
    PatternTiebreak (the LLM adapter) — or, when none is injected, falls
    back to SimpleClass so the classifier can run with no LLM at all. A
    class with no positive fingerprint is SimpleClass.
    """

    def __init__(self, tiebreak: PatternTiebreak | None = None) -> None:
        self._scorer: PatternScorer = PatternScorer()
        self._tiebreak: PatternTiebreak | None = tiebreak

    def classify_all(
        self, catalog: ClassCatalog, layers: dict[str, LayerType],
    ) -> dict[str, PatternName]:
        """Return an FQN -> PatternName map for every catalogued class."""
        return {r.fqn: self._classify(r.fqn, catalog, layers) for r in catalog.classes}

    def _classify(
        self, fqn: str, catalog: ClassCatalog, layers: dict[str, LayerType],
    ) -> PatternName:
        record = next(r for r in catalog.classes if r.fqn == fqn)
        scores = self._scorer.score(record, layers[fqn])
        if not scores:
            return "SimpleClass"
        top = max(scores.values())
        winners = tuple(sorted(p for p, s in scores.items() if s == top))
        if len(winners) == 1:
            return winners[0]
        if self._tiebreak is None:
            return "SimpleClass"
        return self._tiebreak.resolve(record, layers[fqn], winners)
