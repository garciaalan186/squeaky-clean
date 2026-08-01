"""TestRepairRequest: one test file to repair plus its diagnostics."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from squeaky_clean.application.shared.language.language_toolkit import LanguageToolkit


@dataclass(frozen=True)
class TestRepairRequest:
    """One test file to repair, with the diagnostics needed to fix it."""

    project_dir: Path
    rel_path: str
    error_excerpt: str
    toolkit: LanguageToolkit
