"""NullRunLogger: the no-op default when no observability sink is wired."""

from squeaky_clean.domain.interfaces.run_logging.run_logger import RunLogger


class NullRunLogger(RunLogger):
    """No-op RunLogger: the layer-clean default when none is injected."""

    def event(self, kind: str, **fields: object) -> None:
        """Discard the event (no observability sink wired)."""
