"""ModelPricing: per-model USD-per-MTok rates for cost estimation."""

from __future__ import annotations

_RATES: dict[str, tuple[float, float, float, float]] = {
    "claude-haiku-4-5-20251001": (1.0, 5.0, 1.25, 0.10),
    "claude-haiku-4-5":          (1.0, 5.0, 1.25, 0.10),
    "claude-sonnet-4-6":         (3.0, 15.0, 3.75, 0.30),
    "claude-sonnet-4-5":         (3.0, 15.0, 3.75, 0.30),
    "claude-opus-4-7":           (15.0, 75.0, 18.75, 1.50),
    "claude-opus-4-6":           (15.0, 75.0, 18.75, 1.50),
}


def estimate_cost_usd(
    model: str,
    input_tokens: int,
    output_tokens: int,
    cache_creation_tokens: int = 0,
    cache_read_tokens: int = 0,
) -> float:
    """USD cost from token counts. Returns 0.0 for unknown models.

    Rate tuple is (input_per_mtok, output_per_mtok, cache_create_per_mtok,
    cache_read_per_mtok). Input/output rates are standard list pricing;
    cache create is 1.25x input, cache read is 0.1x input (as Anthropic's
    public pricing schedule of April 2026).
    """
    rates = _RATES.get(model)
    if rates is None:
        return 0.0
    in_r, out_r, cc_r, cr_r = rates
    plain_in = max(0, input_tokens - cache_creation_tokens - cache_read_tokens)
    return (
        plain_in * in_r
        + output_tokens * out_r
        + cache_creation_tokens * cc_r
        + cache_read_tokens * cr_r
    ) / 1_000_000.0
