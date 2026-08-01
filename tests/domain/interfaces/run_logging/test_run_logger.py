"""Tests for the RunLogger port (and its compat re-export module)."""

from squeaky_clean.domain.interfaces import run_logger as compat
from squeaky_clean.domain.interfaces.run_logging.null_run_logger import NullRunLogger
from squeaky_clean.domain.interfaces.run_logging.run_logger import RunLogger


class _RecordingLogger(RunLogger):
    def __init__(self) -> None:
        self.events: list[tuple[str, dict[str, object]]] = []

    def event(self, kind: str, **fields: object) -> None:
        self.events.append((kind, fields))


def test_concrete_logger_receives_kind_and_fields() -> None:
    logger = _RecordingLogger()
    logger.event("icp_retry", attempt=2, reason="compile")
    assert logger.events == [("icp_retry", {"attempt": 2, "reason": "compile"})]


def test_compat_module_reexports_both_names() -> None:
    assert compat.RunLogger is RunLogger
    assert compat.NullRunLogger is NullRunLogger
