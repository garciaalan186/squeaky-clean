"""ObligationRepairRequest: inputs to one obligation-repair run."""

from dataclasses import dataclass
from pathlib import Path

from squeaky_clean.application.generation.testgen.test_obligation import TestObligation
from squeaky_clean.application.shared.language.language_toolkit import LanguageToolkit


@dataclass(frozen=True)
class ObligationRepairRequest:
    """Inputs to one obligation-repair run."""

    obligations: tuple[TestObligation, ...]
    output_dir: Path
    toolkit: LanguageToolkit | None
    max_passes: int
