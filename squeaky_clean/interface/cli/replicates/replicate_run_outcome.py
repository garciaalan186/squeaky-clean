"""ReplicateRunOutcome DTO: where a replicate run wrote its summary."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ReplicateRunOutcome:
    """Aggregated multi-replicate result with summary file path."""

    summary_path: Path
    runs: int
