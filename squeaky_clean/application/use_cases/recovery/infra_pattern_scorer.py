"""InfraPatternScorer: fingerprint INFRASTRUCTURE-layer classes to patterns."""

from squeaky_clean.application.dtos.recovery.class_record import ClassRecord
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.pattern_name import PatternName


class InfraPatternScorer:
    """Scores an infra class against Repository / Gateway / Adapter.

    Persistence verbs (save/find/delete) signal Repository; remote-call
    verbs (publish/send/call) signal Gateway; otherwise a class that
    extends a base (implements a port) signals Adapter. Non-infra classes
    score {}.
    """

    _REPO: frozenset[str] = frozenset(
        {"save", "find", "find_by_id", "delete", "get", "list", "upsert"}
    )
    _GATEWAY: frozenset[str] = frozenset(
        {"publish", "send", "call", "request", "invoke", "consume", "subscribe"}
    )

    def score(self, record: ClassRecord, layer: LayerType) -> dict[PatternName, int]:
        """Return candidate infrastructure patterns with confidence scores."""
        if layer is not LayerType.INFRASTRUCTURE:
            return {}
        verbs = {m.split("(", 1)[0] for m in record.methods}
        out: dict[PatternName, int] = {}
        if verbs & self._REPO:
            out["Repository"] = 3
        if verbs & self._GATEWAY:
            out["Gateway"] = 3
        if not out and record.bases:
            out["Adapter"] = 2
        return out
