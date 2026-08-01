"""SecretHit: one detected secret leak with file + line context."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SecretHit:
    """One detected secret leak with file + line context."""

    path: Path
    line: int
    label: str
