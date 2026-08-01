"""FailingTestsRequest: inputs to one failing-test repair pass."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from squeaky_clean.application.shared.language.language_toolkit import LanguageToolkit


@dataclass(frozen=True)
class FailingTestsRequest:
    """Inputs to one failing-test repair pass."""

    raw_output: str
    output_dir: Path
    toolkit: LanguageToolkit | None
