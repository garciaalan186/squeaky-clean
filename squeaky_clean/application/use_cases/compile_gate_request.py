"""CompileGateRequest: inputs to one CompileGate run."""

from dataclasses import dataclass
from pathlib import Path

from squeaky_clean.application.dtos.language_toolkit import LanguageToolkit
from squeaky_clean.application.dtos.module_implementation import ModuleImplementation
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec


@dataclass(frozen=True)
class CompileGateRequest:
    """Inputs to one CompileGate run."""

    implementation: ModuleImplementation
    output_dir: Path
    max_passes: int
    architecture: ArchitectureSpec | None = None
    toolkit: LanguageToolkit | None = None
