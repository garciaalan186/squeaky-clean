"""ModelPricing: per-model USD-per-MTok rates from models.dev/api.json.

Live rates fetched once per process and cached on disk for 24h under
~/.cache/squeaky-clean/. Falls back to a bundled snapshot when offline
or for unknown models. Snapshot reflects Anthropic-direct pricing as of
May 2026 (Opus 4.5+ dropped to $5/$25; earlier $15/$75 tier was Opus 3
and Opus 4.0/4.1).
"""
from __future__ import annotations

import json
import logging
import time
import urllib.request
from pathlib import Path

from squeaky_clean.application.use_cases.atomic_write import atomic_write_text
from squeaky_clean.infrastructure.llm.model_catalog import ModelId

_LOG = logging.getLogger(__name__)

_FALLBACK: dict[str, tuple[float, float, float, float]] = {
    # Current models — keyed off the ModelId single source of truth.
    ModelId.HAIKU:      (1.0, 5.0, 1.25, 0.10),
    ModelId.SONNET:     (3.0, 15.0, 3.75, 0.30),
    ModelId.OPUS:       (5.0, 25.0, 6.25, 0.50),
    # Legacy models — retained only to price historical run manifests.
    ModelId.HAIKU_4_5_ALIAS: (1.0, 5.0, 1.25, 0.10),
    ModelId.SONNET_4_6:      (3.0, 15.0, 3.75, 0.30),
    ModelId.SONNET_4_5:      (3.0, 15.0, 3.75, 0.30),
    ModelId.OPUS_4_7:        (5.0, 25.0, 6.25, 0.50),
    ModelId.OPUS_4_6:        (5.0, 25.0, 6.25, 0.50),
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
            atomic_write_text(_CACHE, json.dumps(data))
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


def _resolve_rates(model: str) -> tuple[float, float, float, float]:
    """Known rate for ``model``, else a conservative family fallback.

    An unknown model MUST NOT price at $0 — that silently defeats budget
    accounting (R0.10). We infer the family from the id substring and use its
    rates, defaulting to the most expensive tier (Opus) so an unrecognised
    future model over-estimates rather than under-charges. Always warns loudly.
    """
    rates = _live_rates().get(model) or _FALLBACK.get(model)
    if rates is not None:
        return rates
    lower = model.lower()
    if "haiku" in lower:
        family, fallback = "haiku", _FALLBACK[ModelId.HAIKU]
    elif "sonnet" in lower:
        family, fallback = "sonnet", _FALLBACK[ModelId.SONNET]
    else:
        family, fallback = "opus (conservative default)", _FALLBACK[ModelId.OPUS]
    _LOG.warning(
        "unknown model %r for pricing; using %s-family rates to avoid $0 "
        "budget accounting", model, family,
    )
    return fallback


def is_priced(model: str) -> bool:
    """True iff ``model`` has an exact rate (no family fallback).

    Budget accounting wants a conservative estimate for unknown models
    (``estimate_cost_usd``), but reporting paths (e.g. cache-savings) prefer
    an honest $0 over a guessed rate — this predicate lets them tell the two
    situations apart.
    """
    return (_live_rates().get(model) or _FALLBACK.get(model)) is not None


def estimate_cost_usd(
    model: str,
    input_tokens: int,
    output_tokens: int,
    cache_creation_tokens: int = 0,
    cache_read_tokens: int = 0,
) -> float:
    """USD cost from token counts. Tuple is (in, out, cache_write,
    cache_read) per-MTok. Unknown models fall back to a conservative
    same-family rate (never a silent $0) — see ``_resolve_rates``."""
    in_r, out_r, cw_r, cr_r = _resolve_rates(model)
    plain_in = max(0, input_tokens - cache_creation_tokens - cache_read_tokens)
    return (
        plain_in * in_r
        + output_tokens * out_r
        + cache_creation_tokens * cw_r
        + cache_read_tokens * cr_r
    ) / 1_000_000.0
