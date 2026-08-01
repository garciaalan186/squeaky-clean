"""Tests for the LifecycleLog port (R6.2 DIP fix)."""

from squeaky_clean.domain.interfaces.lifecycle_log import LifecycleLog
from squeaky_clean.infrastructure.observability.lifecycle_timestamp_log import (
    LifecycleTimestampLog,
)


def test_infrastructure_log_satisfies_the_port(tmp_path) -> None:  # noqa: ANN001
    log: LifecycleLog = LifecycleTimestampLog(tmp_path)
    log.record("a")
    log.record_fields("b", {"k": 1})
    assert log.elapsed_ms("a", "b") is not None
