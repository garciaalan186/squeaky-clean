"""RetryPolicy DTO: bounded retry + exponential backoff configuration."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RetryPolicy:
    """Immutable retry configuration for ICP and fixer-pass loops.

    ``max_transport_retries`` bounds the low-level gateway wrapper that retries
    *transient* transport failures (OSError, empty non-zero exit, timeout,
    malformed result JSON) at EVERY tier, independent of the ICP parse-retry
    loop layered on top. ``jitter_ratio`` spreads concurrent retries so the
    four ICP threads do not re-hammer the backend in lockstep (thundering herd).
    """

    max_icp_retries: int = 1
    max_fixer_passes: int = 1
    backoff_base_seconds: float = 1.0
    backoff_multiplier: float = 2.0
    max_transport_retries: int = 2
    jitter_ratio: float = 0.1

    def __post_init__(self) -> None:
        """Validate non-negativity and multiplier >= 1.0."""
        if self.max_icp_retries < 0:
            raise ValueError("max_icp_retries must be >= 0")
        if self.max_fixer_passes < 0:
            raise ValueError("max_fixer_passes must be >= 0")
        if self.backoff_base_seconds < 0:
            raise ValueError("backoff_base_seconds must be >= 0")
        if self.backoff_multiplier < 1.0:
            raise ValueError("backoff_multiplier must be >= 1.0")
        if self.max_transport_retries < 0:
            raise ValueError("max_transport_retries must be >= 0")
        if not 0.0 <= self.jitter_ratio <= 1.0:
            raise ValueError("jitter_ratio must be in [0.0, 1.0]")

    def delay_for(self, attempt: int) -> float:
        """Return seconds to sleep before retry ``attempt`` (0-indexed)."""
        if attempt < 0:
            return 0.0
        return self.backoff_base_seconds * (self.backoff_multiplier ** attempt)

    def jittered_delay_for(self, attempt: int, rand: float) -> float:
        """``delay_for`` plus ``rand`` * ``jitter_ratio`` of the base delay.

        ``rand`` is a caller-supplied value in [0.0, 1.0) (e.g. ``random()``),
        kept as a parameter so the jitter is deterministic under test.
        """
        base = self.delay_for(attempt)
        return base + (rand * self.jitter_ratio * base)
