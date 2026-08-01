"""Tests for CacheEntry + parse_cache_entry (R6.8: rejections carry reasons)."""

from datetime import datetime, timedelta, timezone

from squeaky_clean.infrastructure.techspec.techspec_cache_entry import (
    CacheEntry,
    parse_cache_entry,
)

_NOW = datetime(2026, 7, 1, tzinfo=timezone.utc)


def _entry(expires_offset_days: int) -> CacheEntry:
    return CacheEntry(
        spec={"schema_version": "v1"},
        fetched_at=_NOW - timedelta(days=30),
        expires_at=_NOW + timedelta(days=expires_offset_days),
        content_hash="sha256:abc",
    )


def test_freshness_predicates() -> None:
    assert _entry(expires_offset_days=1).is_fresh(_NOW)
    assert not _entry(expires_offset_days=-1).is_fresh(_NOW)
    # Expired 10 days ago but inside the 30 // 2 + 1 = 16-day grace window.
    assert _entry(expires_offset_days=-10).is_stale_tolerant(_NOW, 30)
    assert not _entry(expires_offset_days=-20).is_stale_tolerant(_NOW, 30)


def _parse(data: dict[str, object]) -> tuple[CacheEntry | None, list[str]]:
    reasons: list[str] = []
    return parse_cache_entry(data, reasons.append), reasons


def test_parse_valid_payload() -> None:
    entry, reasons = _parse({
        "spec": {"schema_version": "v1"},
        "fetched_at": _NOW.isoformat(),
        "expires_at": (_NOW + timedelta(days=30)).isoformat(),
        "content_hash": "sha256:abc",
    })
    assert entry is not None and reasons == []
    assert entry.content_hash == "sha256:abc"


def test_parse_rejections_report_a_reason() -> None:
    cases: list[dict[str, object]] = [
        {},  # no spec
        {"spec": {"schema_version": "v0"}},  # wrong schema version
        {"spec": {"schema_version": "v1"}, "fetched_at": "junk"},  # bad dates
    ]
    for data in cases:
        entry, reasons = _parse(data)
        assert entry is None
        assert len(reasons) == 1 and reasons[0]
