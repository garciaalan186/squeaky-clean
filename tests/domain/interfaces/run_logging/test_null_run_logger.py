"""Tests for NullRunLogger."""

from squeaky_clean.domain.interfaces.run_logging.null_run_logger import NullRunLogger
from squeaky_clean.domain.interfaces.run_logging.run_logger import RunLogger


def test_is_a_run_logger() -> None:
    assert isinstance(NullRunLogger(), RunLogger)


def test_event_is_a_silent_no_op() -> None:
    logger = NullRunLogger()
    assert logger.event("anything", detail="ignored") is None
