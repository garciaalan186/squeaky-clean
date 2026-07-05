"""PatternTiebreak port: resolve a multi-way pattern tie to one pattern."""

from abc import ABC, abstractmethod

from squeaky_clean.application.dtos.recovery.class_record import ClassRecord
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.pattern_name import PatternName


class PatternTiebreak(ABC):
    """Port for breaking a fingerprint tie among candidate patterns.

    Injected into PatternClassifier so the deterministic fingerprint path
    stays free of any LLM dependency: with no tiebreak the classifier
    falls back to SimpleClass on a tie; with one (the LLM-backed adapter)
    it consults an agent constrained to the candidate set.
    """

    @abstractmethod
    def resolve(
        self,
        record: ClassRecord,
        layer: LayerType,
        candidates: tuple[PatternName, ...],
    ) -> PatternName:
        """Return one pattern from ``candidates`` (or SimpleClass fallback)."""
