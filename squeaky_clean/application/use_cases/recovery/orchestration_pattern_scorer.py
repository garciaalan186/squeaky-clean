"""OrchestrationPatternScorer: fingerprint APPLICATION/INTERFACE classes."""

from squeaky_clean.application.dtos.recovery.class_record import ClassRecord
from squeaky_clean.domain.value_objects.layer_type import LayerType
from squeaky_clean.domain.value_objects.pattern_name import PatternName


class OrchestrationPatternScorer:
    """Scores application/interface classes against UseCase / Presenter.

    An application class whose sole entry point is an orchestration verb
    (execute/handle/run) — or that exposes a single method — signals
    UseCase. An interface class with view-rendering verbs signals
    Presenter. Other layers score {}.
    """

    _USE_CASE: frozenset[str] = frozenset({"execute", "handle", "run", "perform"})
    _PRESENT: frozenset[str] = frozenset({"render", "present", "format", "view"})

    def score(self, record: ClassRecord, layer: LayerType) -> dict[PatternName, int]:
        """Return candidate orchestration patterns with confidence scores."""
        verbs = {m.split("(", 1)[0] for m in record.methods}
        out: dict[PatternName, int] = {}
        if layer is LayerType.APPLICATION:
            if verbs & self._USE_CASE:
                out["UseCase"] = 3
            elif len(record.methods) == 1:
                out["UseCase"] = 2
        if layer is LayerType.INTERFACE and verbs & self._PRESENT:
            out["Presenter"] = 2
        return out
