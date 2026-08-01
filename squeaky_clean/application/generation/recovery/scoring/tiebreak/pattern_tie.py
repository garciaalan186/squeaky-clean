"""PatternTie: a fingerprint tie among candidate patterns for one class."""

from dataclasses import dataclass

from squeaky_clean.application.generation.recovery.extraction.class_record import ClassRecord
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.pattern_name import PatternName


@dataclass(frozen=True)
class PatternTie:
    """The unresolved classification of one class: who tied, and where.

    Produced by PatternClassifier when two or more patterns share the top
    fingerprint score; consumed by PatternTiebreak adapters, which also
    carry it into prompt assembly. ``candidates`` is the tied set, sorted
    deterministically by the classifier.
    """

    record: ClassRecord
    layer: LayerType
    candidates: tuple[PatternName, ...]
