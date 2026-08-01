"""CachedGenerateTestArchitecture: returns the cached merged TestArchitecture once."""

from __future__ import annotations

from squeaky_clean.application.evaluation.eval.resume.resume_per_arch_once import PerArchOnce
from squeaky_clean.application.generation.testgen.test_architecture import TestArchitecture
from squeaky_clean.application.generation.testgen.test_architecture_context import (
    TestArchitectureContext,
)
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec


class CachedGenerateTestArchitecture:
    """Returns the cached merged TestArchitecture once (then empty)."""

    def __init__(
        self, cached: TestArchitecture, arch: ArchitectureSpec,
    ) -> None:
        self._gate: PerArchOnce = PerArchOnce(cached, arch)

    def execute(self, context: TestArchitectureContext) -> TestArchitecture:
        return self._gate.take(context.module)
