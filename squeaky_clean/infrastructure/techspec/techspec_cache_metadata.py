"""TechSpecCacheMetadata: read/write cache entries with TTL bookkeeping (H4)."""

import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import cast

from squeaky_clean.domain.interfaces.run_logger import NullRunLogger, RunLogger
from squeaky_clean.infrastructure.techspec.techspec_cache_entry import (
    CacheEntry,
    parse_cache_entry,
)


class TechSpecCacheMetadata:
    """Reads + writes cache files with TTL/hash/source-url metadata.

    ``read`` returns None for both a clean miss (no file) and a rejected
    entry — but a rejection is never silent: every invalid entry emits a
    ``techspec_cache_rejected`` event with the reason (R6.8).
    """

    def __init__(
        self, ttl_days: int = 30, *, run_logger: RunLogger | None = None,
    ) -> None:
        self.ttl_days: int = int(ttl_days)
        self._log: RunLogger = run_logger or NullRunLogger()

    def write(
        self, path: Path, spec: dict[str, object],
        source_urls: tuple[str, ...], now: datetime,
    ) -> None:
        """Write a cache entry, including TTL window + content-hash."""
        path.parent.mkdir(parents=True, exist_ok=True)
        body = json.dumps(spec, sort_keys=True).encode("utf-8")
        payload = {
            "fetched_at": now.isoformat(),
            "expires_at": (now + timedelta(days=self.ttl_days)).isoformat(),
            "source_urls": list(source_urls),
            "content_hash": "sha256:" + hashlib.sha256(body).hexdigest(),
            "spec": spec,
        }
        path.write_text(json.dumps(payload, indent=2, sort_keys=True))

    def read(self, path: Path) -> CacheEntry | None:
        """Return parsed CacheEntry, or None on miss (rejections are logged)."""
        if not path.is_file():
            return None
        data = self._load(path)
        if data is None:
            return None
        return parse_cache_entry(
            data, lambda reason: self._reject(path, reason),
        )

    def _load(self, path: Path) -> dict[str, object] | None:
        reason: str | None = None
        loaded: object = None
        try:
            loaded = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            reason = f"unreadable: {exc}"
        if reason is None and not isinstance(loaded, dict):
            reason = "not a JSON object"
        if reason is not None:
            self._reject(path, reason)
            return None
        return cast(dict[str, object], loaded)

    def _reject(self, path: Path, reason: str) -> None:
        """Log one invalid-entry event; the entry is then treated as a miss."""
        self._log.event(
            "techspec_cache_rejected", path=str(path), reason=reason,
        )

    @staticmethod
    def now_utc() -> datetime:
        """Return tz-aware UTC now (single seam for testability)."""
        return datetime.now(timezone.utc)
