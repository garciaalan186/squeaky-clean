"""NotationScanTarget: value-object describing a balanced-scan target."""

from dataclasses import dataclass


@dataclass(frozen=True)
class NotationScanTarget:
    """Text plus the opener/closer pair to balance-scan for."""

    text: str
    opener: str
    closer: str
