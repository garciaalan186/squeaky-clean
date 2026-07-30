"""Unit tests for LifecycleTimestampLog."""

import json
from pathlib import Path

from squeaky_clean.infrastructure.observability.lifecycle_timestamp_log import (
    LifecycleTimestampLog,
)


def test_record_appends_timestamped_event(tmp_path: Path) -> None:
    log = LifecycleTimestampLog(tmp_path)
    log.record("squib_parse_start")
    lines = (tmp_path / "squib_lifecycle.jsonl").read_text().splitlines()
    assert len(lines) == 1
    payload = json.loads(lines[0])
    assert payload["event"] == "squib_parse_start"
    assert isinstance(payload["ts"], float)


def test_record_fields_merges_extra_fields(tmp_path: Path) -> None:
    log = LifecycleTimestampLog(tmp_path)
    log.record_fields("tests_complete", {"all_passed": True, "failed": 0})
    payload = json.loads((tmp_path / "squib_lifecycle.jsonl").read_text())
    assert payload["event"] == "tests_complete"
    assert payload["all_passed"] is True
    assert payload["failed"] == 0
    assert "ts" in payload


def test_records_accumulate_in_order(tmp_path: Path) -> None:
    log = LifecycleTimestampLog(tmp_path)
    log.record("squib_parse_start")
    log.record("build_complete")
    lines = (tmp_path / "squib_lifecycle.jsonl").read_text().splitlines()
    events = [json.loads(line)["event"] for line in lines]
    assert events == ["squib_parse_start", "build_complete"]


def test_elapsed_ms_between_recorded_events(tmp_path: Path) -> None:
    log = LifecycleTimestampLog(tmp_path)
    log.record("squib_parse_start")
    log.record_fields("tests_complete", {"all_passed": True})
    elapsed = log.elapsed_ms("squib_parse_start", "tests_complete")
    assert elapsed is not None
    assert elapsed >= 0


def test_elapsed_ms_none_when_event_missing(tmp_path: Path) -> None:
    log = LifecycleTimestampLog(tmp_path)
    log.record("squib_parse_start")
    assert log.elapsed_ms("squib_parse_start", "tests_complete") is None
