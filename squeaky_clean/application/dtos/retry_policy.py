"""RetryPolicy DTO: bounded retry + exponential backoff configuration."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RetryPolicy:
    """Immutable retry configuration for ICP and fixer-pass loops."""

    max_icp_retries: int = 1
    max_fixer_passes: int = 1
    backoff_base_seconds: float = 1.0
    backoff_multiplier: float = 2.0

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

    def delay_for(self, attempt: int) -> float:
        """Return seconds to sleep before retry ``attempt`` (0-indexed)."""
        if attempt < 0:
            return 0.0
        return self.backoff_base_seconds * (self.backoff_multiplier ** attempt)
