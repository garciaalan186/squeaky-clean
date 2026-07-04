"""ModelPricing: per-model USD-per-MTok rates from models.dev/api.json.

Live rates fetched once per process and cached on disk for 24h under
~/.cache/squeaky-clean/. Falls back to a bundled snapshot when offline
or for unknown models. Snapshot reflects Anthropic-direct pricing as of
May 2026 (Opus 4.5+ dropped to $5/$25; earlier $15/$75 tier was Opus 3
and Opus 4.0/4.1).
"""
from __future__ import annotations

import json
import time
import urllib.request
from pathlib import Path

_FALLBACK: dict[str, tuple[float, float, float, float]] = {
    "claude-haiku-4-5-20251001": (1.0, 5.0, 1.25, 0.10),
    "claude-haiku-4-5":          (1.0, 5.0, 1.25, 0.10),
    "claude-sonnet-4-6":         (3.0, 15.0, 3.75, 0.30),
    "claude-sonnet-4-5":         (3.0, 15.0, 3.75, 0.30),
    "claude-opus-4-7":           (5.0, 25.0, 6.25, 0.50),
    "claude-opus-4-6":           (5.0, 25.0, 6.25, 0.50),
}

_CACHE = Path.home() / ".cache" / "squeaky-clean" / "models_dev.json"
_TTL_S = 86_400
_URL = "https://models.dev/api.json"
_LIVE: dict[str, tuple[float, float, float, float]] | None = None


def _load_cached() -> dict | None:
    if not _CACHE.exists():
        return None
    try:
        return json.loads(_CACHE.read_text())
    except (OSError, json.JSONDecodeError):
        return None


def _live_rates() -> dict[str, tuple[float, float, float, float]]:
    global _LIVE
    if _LIVE is not None:
        return _LIVE
    fresh = _CACHE.exists() and (time.time() - _CACHE.stat().st_mtime) < _TTL_S
    data = _load_cached() if fresh else None
    if data is None:
        try:
            req = urllib.request.Request(_URL, headers={"User-Agent": "squeaky-clean"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
            _CACHE.parent.mkdir(parents=True, exist_ok=True)
            _CACHE.write_text(json.dumps(data))
        except (OSError, json.JSONDecodeError, ValueError):
            data = _load_cached()
    rates: dict[str, tuple[float, float, float, float]] = {}
    if data is not None:
        for mid, m in data.get("anthropic", {}).get("models", {}).items():
            c = m.get("cost") or {}
            try:
                rates[mid] = (
                    float(c.get("input", 0.0)), float(c.get("output", 0.0)),
                    float(c.get("cache_write", 0.0)), float(c.get("cache_read", 0.0)),
                )
            except (TypeError, ValueError):
                continue
    _LIVE = rates
    return rates


def estimate_cost_usd(
    model: str,
    input_tokens: int,
    output_tokens: int,
    cache_creation_tokens: int = 0,
    cache_read_tokens: int = 0,
) -> float:
    """USD cost from token counts. Tuple is (in, out, cache_write,
    cache_read) per-MTok. Returns 0.0 for unknown models."""
    rates = _live_rates().get(model) or _FALLBACK.get(model)
    if rates is None:
        return 0.0
    in_r, out_r, cw_r, cr_r = rates
    plain_in = max(0, input_tokens - cache_creation_tokens - cache_read_tokens)
    return (
        plain_in * in_r
        + output_tokens * out_r
        + cache_creation_tokens * cw_r
        + cache_read_tokens * cr_r
    ) / 1_000_000.0
