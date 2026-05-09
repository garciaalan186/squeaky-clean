"""TechSpecCacheMetadata: read/write cache entries with TTL bookkeeping (H4)."""

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import cast

_CURRENT_SCHEMA_VERSION: str = "v1"


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


class TechSpecCacheMetadata:
    """Reads + writes cache files with TTL/hash/source-url metadata."""

    def __init__(self, ttl_days: int = 30) -> None:
        self.ttl_days: int = int(ttl_days)

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
        """Return parsed CacheEntry or None on any read failure."""
        if not path.is_file():
            return None
        try:
            data = cast(dict[str, object], json.loads(path.read_text()))
        except (OSError, json.JSONDecodeError):
            return None
        spec = data.get("spec")
        if not isinstance(spec, dict):
            return None
        spec_dict = cast(dict[str, object], spec)
        if spec_dict.get("schema_version") != _CURRENT_SCHEMA_VERSION:
            return None
        try:
            fetched = datetime.fromisoformat(str(data["fetched_at"]))
            expires = datetime.fromisoformat(str(data["expires_at"]))
        except (KeyError, ValueError, TypeError):
            return None
        return CacheEntry(
            spec=spec_dict, fetched_at=fetched, expires_at=expires,
            content_hash=str(data.get("content_hash") or ""),
        )

    @staticmethod
    def now_utc() -> datetime:
        """Return tz-aware UTC now (single seam for testability)."""
        return datetime.now(timezone.utc)
