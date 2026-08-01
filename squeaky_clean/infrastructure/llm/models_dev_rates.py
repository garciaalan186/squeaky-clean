"""Live per-model rates from models.dev/api.json (24h on-disk cache).

Fetched once per process; falls back to whatever cached payload exists
when offline. Consumers (``model_pricing``) overlay these live rates on
the bundled snapshot, so an empty dict here is always safe.
"""

from __future__ import annotations

import json
import time
import urllib.request
from pathlib import Path

from squeaky_clean.application.shared.io.atomic_write import atomic_write_text
from squeaky_clean.domain.interfaces.run_logger import NullRunLogger, RunLogger

_CACHE = Path.home() / ".cache" / "squeaky-clean" / "models_dev.json"
_TTL_S = 86_400
_URL = "https://models.dev/api.json"
_LIVE: dict[str, tuple[float, float, float, float]] | None = None


def _load_cached(log: RunLogger) -> dict[str, object] | None:
    if not _CACHE.exists():
        return None
    try:
        loaded = json.loads(_CACHE.read_text())
    except (OSError, json.JSONDecodeError) as exc:
        log.event("pricing_cache_unreadable", path=str(_CACHE), error=str(exc))
        return None
    return loaded if isinstance(loaded, dict) else None


def live_rates(
    *, logger: RunLogger | None = None,
) -> dict[str, tuple[float, float, float, float]]:
    """Anthropic (in, out, cache_write, cache_read) per-MTok by model id."""
    global _LIVE
    log = logger or NullRunLogger()
    if _LIVE is not None:
        return _LIVE
    fresh = _CACHE.exists() and (time.time() - _CACHE.stat().st_mtime) < _TTL_S
    data = _load_cached(log) if fresh else None
    if data is None:
        try:
            req = urllib.request.Request(_URL, headers={"User-Agent": "squeaky-clean"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
            atomic_write_text(_CACHE, json.dumps(data))
        except (OSError, json.JSONDecodeError, ValueError):
            data = _load_cached(log)
    rates: dict[str, tuple[float, float, float, float]] = {}
    anthropic = data.get("anthropic") if data is not None else None
    models = anthropic.get("models") if isinstance(anthropic, dict) else None
    if isinstance(models, dict):
        for mid, m in models.items():
            c = m.get("cost") if isinstance(m, dict) else None
            if not isinstance(c, dict):
                continue
            try:
                rates[str(mid)] = (
                    float(c.get("input", 0.0)), float(c.get("output", 0.0)),
                    float(c.get("cache_write", 0.0)), float(c.get("cache_read", 0.0)),
                )
            except (TypeError, ValueError):
                continue
    _LIVE = rates
    return rates
