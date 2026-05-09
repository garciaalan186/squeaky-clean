"""IntegrationRequest DTO: inputs for IntegrateModule.execute()."""

from dataclasses import dataclass
from pathlib import Path

from squeaky_clean.application.dtos.module_implementation import ModuleImplementation
from squeaky_clean.application.dtos.test_architecture import TestArchitecture


@dataclass(frozen=True)
class IntegrationRequest:
    """Immutable bundle of what IntegrateModule needs to write a project.

    `implementation` carries all ICP-produced source for the module.
    `test_architecture` carries the parallel set of pytest skeletons.
    `security_test_architecture` carries security test skeletons (or None).
    `output_dir` is the root directory under which ``src/`` and
    ``tests/`` will be materialised.
    """

    implementation: ModuleImplementation
    test_architecture: TestArchitecture
    output_dir: Path
    security_test_architecture: TestArchitecture | None = None
