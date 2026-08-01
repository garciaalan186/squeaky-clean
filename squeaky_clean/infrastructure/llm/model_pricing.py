"""ModelPricing: per-model USD-per-MTok rates from models.dev/api.json.

Live rates come from ``models_dev_rates`` (fetched once per process,
cached on disk for 24h under ~/.cache/squeaky-clean/). Falls back to a
bundled snapshot when offline or for unknown models. Snapshot reflects
Anthropic-direct pricing as of May 2026 (Opus 4.5+ dropped to $5/$25;
earlier $15/$75 tier was Opus 3 and Opus 4.0/4.1).
"""
from __future__ import annotations

from squeaky_clean.domain.interfaces.run_logger import NullRunLogger, RunLogger
from squeaky_clean.infrastructure.llm.model_catalog import ModelId
from squeaky_clean.infrastructure.llm.models_dev_rates import live_rates

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


def _resolve_rates(model: str, log: RunLogger) -> tuple[float, float, float, float]:
    """Known rate for ``model``, else a conservative family fallback.

    An unknown model MUST NOT price at $0 — that silently defeats budget
    accounting (R0.10). We infer the family from the id substring and use its
    rates, defaulting to the most expensive tier (Opus) so an unrecognised
    future model over-estimates rather than under-charges. Always warns loudly.
    """
    rates = live_rates(logger=log).get(model) or _FALLBACK.get(model)
    if rates is not None:
        return rates
    lower = model.lower()
    if "haiku" in lower:
        family, fallback = "haiku", _FALLBACK[ModelId.HAIKU]
    elif "sonnet" in lower:
        family, fallback = "sonnet", _FALLBACK[ModelId.SONNET]
    else:
        family, fallback = "opus (conservative default)", _FALLBACK[ModelId.OPUS]
    log.event(
        "pricing_unknown_model", model=model, family_used=family,
        detail="family rates applied to avoid $0 budget accounting (R0.10)",
    )
    return fallback


def is_priced(model: str) -> bool:
    """True iff ``model`` has an exact rate (no family fallback).

    Budget accounting wants a conservative estimate for unknown models
    (``estimate_cost_usd``), but reporting paths (e.g. cache-savings) prefer
    an honest $0 over a guessed rate — this predicate lets them tell the two
    situations apart.
    """
    return (live_rates().get(model) or _FALLBACK.get(model)) is not None


def estimate_cost_usd(
    model: str,
    input_tokens: int,
    output_tokens: int,
    cache_creation_tokens: int = 0,
    cache_read_tokens: int = 0,
    *,
    logger: RunLogger | None = None,
) -> float:
    """USD cost from token counts. Tuple is (in, out, cache_write,
    cache_read) per-MTok. Unknown models fall back to a conservative
    same-family rate (never a silent $0) — see ``_resolve_rates``.
    ``logger`` receives the unknown-model event; production callers
    thread the run's RunLogger (R6.12 DIP residue close-out)."""
    in_r, out_r, cw_r, cr_r = _resolve_rates(model, logger or NullRunLogger())
    plain_in = max(0, input_tokens - cache_creation_tokens - cache_read_tokens)
    return (
        plain_in * in_r
        + output_tokens * out_r
        + cache_creation_tokens * cw_r
        + cache_read_tokens * cr_r
    ) / 1_000_000.0
