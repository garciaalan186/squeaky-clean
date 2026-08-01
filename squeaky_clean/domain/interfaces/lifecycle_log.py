"""LifecycleLog port: run-lifecycle timestamps the pipeline stages record."""

from __future__ import annotations

from typing import Protocol


class LifecycleLog(Protocol):
    """Structural port for LifecycleTimestampLog (R6.2 DIP fix).

    PipelineContext types against this so application stages never import
    the infrastructure implementation.
    """

    def record(self, event: str) -> None:
        """Record a named lifecycle event at the current time."""
        ...

    def record_fields(self, event: str, fields: dict[str, object]) -> None:
        """Record a named event carrying extra fields."""
        ...

    def elapsed_ms(self, start_event: str, end_event: str) -> int | None:
        """Milliseconds between two recorded events, or None if missing."""
        ...
