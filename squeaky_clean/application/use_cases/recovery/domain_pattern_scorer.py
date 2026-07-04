"""DomainPatternScorer: fingerprint DOMAIN-layer classes to patterns."""

from squeaky_clean.application.dtos.recovery.class_record import ClassRecord
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.pattern_name import PatternName


class DomainPatternScorer:
    """Scores a domain class against Entity / ValueObject / DomainEvent.

    A first-class ``id`` field signals Entity; its absence with immutable
    shape signals ValueObject; a name ending in ``Event`` signals
    DomainEvent. Scores are small integers — the classifier compares them
    and escalates ties to the LLM tie-break. Non-domain classes score {}.
    """

    def score(self, record: ClassRecord, layer: LayerType) -> dict[PatternName, int]:
        """Return candidate domain patterns with confidence scores."""
        if layer is not LayerType.DOMAIN:
            return {}
        out: dict[PatternName, int] = {}
        if record.fqn.rsplit(".", 1)[-1].endswith("Event"):
            out["DomainEvent"] = 3
        if self._has_id(record):
            out["Entity"] = 2 + (1 if record.methods else 0)
        else:
            out["ValueObject"] = 2
        return out

    def _has_id(self, record: ClassRecord) -> bool:
        return any(f.split(":", 1)[0].strip() == "id" for f in record.fields)
