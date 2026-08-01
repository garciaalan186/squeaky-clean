"""CacheEntry: one TechSpec cache record with TTL freshness predicates (H4)."""

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import cast

CURRENT_SCHEMA_VERSION: str = "v1"


@dataclass(frozen=True)
class CacheEntry:
    """One cache record loaded from disk: spec + freshness metadata."""

    spec: dict[str, object]
    fetched_at: datetime
    expires_at: datetime
    content_hash: str

    def is_fresh(self, now: datetime) -> bool:
        """True iff now < expires_at."""
        return now < self.expires_at

    def is_stale_tolerant(self, now: datetime, ttl_days: int) -> bool:
        """True iff now < expires_at + 0.5 * TTL (1.5x grace window)."""
        return now < self.expires_at + timedelta(days=ttl_days // 2 + 1)


def parse_cache_entry(
    data: dict[str, object], reject: Callable[[str], None],
) -> CacheEntry | None:
    """Build a CacheEntry from a raw cache payload.

    Invalid payloads call ``reject(reason)`` and yield None — the caller
    decides where the reason goes (RunLogger event); nothing is swallowed
    silently (R6.8).
    """
    spec = data.get("spec")
    if not isinstance(spec, dict):
        reject("spec missing or not a JSON object")
        return None
    spec_dict = cast(dict[str, object], spec)
    if spec_dict.get("schema_version") != CURRENT_SCHEMA_VERSION:
        reject("schema_version mismatch")
        return None
    fetched = expires = None
    try:
        fetched = datetime.fromisoformat(str(data["fetched_at"]))
        expires = datetime.fromisoformat(str(data["expires_at"]))
    except (KeyError, ValueError, TypeError) as exc:
        reject(f"bad timestamps: {exc}")
    if fetched is None or expires is None:
        return None
    return CacheEntry(
        spec=spec_dict, fetched_at=fetched, expires_at=expires,
        content_hash=str(data.get("content_hash") or ""),
    )
