"""RunLogger port: structured event sink for pipeline observability."""

from abc import ABC, abstractmethod


class RunLogger(ABC):
    """Port for emitting structured run events.

    Shaped after the infrastructure ``JSONLogger.event`` signature so the
    application layer can record operational events without importing a
    concrete logger. ``NullRunLogger`` is the safe default; the composition
    root injects the real sink.
    """

    @abstractmethod
    def event(self, kind: str, **fields: object) -> None:
        """Emit a structured event named ``kind`` with arbitrary fields."""


class NullRunLogger(RunLogger):
    """No-op RunLogger: the layer-clean default when none is injected."""

    def event(self, kind: str, **fields: object) -> None:
        """Discard the event (no observability sink wired)."""
