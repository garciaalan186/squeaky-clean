"""Tests for TechSpecCacheMetadata (R6.8: cache rejections are logged)."""

from pathlib import Path

from squeaky_clean.domain.interfaces.run_logger import RunLogger
from squeaky_clean.infrastructure.techspec.techspec_cache_metadata import (
    TechSpecCacheMetadata,
)


class _FakeRunLogger(RunLogger):
    def __init__(self) -> None:
        self.events: list[tuple[str, dict[str, object]]] = []

    def event(self, kind: str, **fields: object) -> None:
        self.events.append((kind, dict(fields)))


def test_roundtrip_write_read(tmp_path: Path) -> None:
    log = _FakeRunLogger()
    cache = TechSpecCacheMetadata(30, run_logger=log)
    target = tmp_path / "cat" / "tech" / "v1.json"
    cache.write(target, cache.entry_for({"schema_version": "v1"}, ("https://x",)))
    entry = cache.read(target)
    assert entry is not None and entry.spec == {"schema_version": "v1"}
    assert log.events == []


def test_missing_file_is_a_silent_clean_miss(tmp_path: Path) -> None:
    log = _FakeRunLogger()
    cache = TechSpecCacheMetadata(30, run_logger=log)
    assert cache.read(tmp_path / "absent.json") is None
    assert log.events == []


def test_corrupt_file_is_logged_not_swallowed(tmp_path: Path) -> None:
    log = _FakeRunLogger()
    cache = TechSpecCacheMetadata(30, run_logger=log)
    target = tmp_path / "bad.json"
    target.write_text("{not json")
    assert cache.read(target) is None
    kinds = [k for k, _ in log.events]
    assert kinds == ["techspec_cache_rejected"]
    assert "unreadable" in str(log.events[0][1]["reason"])


def test_schema_mismatch_is_logged(tmp_path: Path) -> None:
    log = _FakeRunLogger()
    cache = TechSpecCacheMetadata(30, run_logger=log)
    target = tmp_path / "old.json"
    cache.write(target, cache.entry_for({"schema_version": "v0"}))
    assert cache.read(target) is None
    assert log.events[0][0] == "techspec_cache_rejected"
    assert "schema_version" in str(log.events[0][1]["reason"])
