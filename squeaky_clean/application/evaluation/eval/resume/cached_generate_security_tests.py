"""CachedGenerateSecurityTests: returns the cached security TestArchitecture once."""

from __future__ import annotations

from squeaky_clean.application.evaluation.eval.resume.resume_per_arch_once import PerArchOnce
from squeaky_clean.application.generation.security.security_test_context import SecurityTestContext
from squeaky_clean.application.generation.testgen.test_architecture import TestArchitecture
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec


class CachedGenerateSecurityTests:
    """Returns the cached merged security TestArchitecture once."""

    def __init__(
        self, cached: TestArchitecture, arch: ArchitectureSpec,
    ) -> None:
        self._gate: PerArchOnce = PerArchOnce(cached, arch)

    def execute(self, context: SecurityTestContext) -> TestArchitecture:
        return self._gate.take(context.module)
