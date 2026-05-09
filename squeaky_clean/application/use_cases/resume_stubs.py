"""Cached stub collaborators used by ResumeStubFactory (G3 — pipeline stubs)."""

from __future__ import annotations

from squeaky_clean.application.dtos.module_implementation import ModuleImplementation
from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.application.dtos.security_review import SecurityReview
from squeaky_clean.application.dtos.security_review_context import SecurityReviewContext
from squeaky_clean.application.dtos.security_test_context import SecurityTestContext
from squeaky_clean.application.dtos.test_architecture import TestArchitecture
from squeaky_clean.application.dtos.test_architecture_context import TestArchitectureContext
from squeaky_clean.application.use_cases.resume_per_arch_once import PerArchOnce
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec


class CachedDesignArchitecture:
    """Stand-in for DesignArchitecture that returns a cached spec."""

    def __init__(self, arch: ArchitectureSpec) -> None:
        self._arch: ArchitectureSpec = arch
        self.last_raw_notation: str = ""

    def execute(self, problem: ProblemSpec) -> ArchitectureSpec:
        del problem
        return self._arch


class CachedGenerateTestArchitecture:
    """Returns the cached merged TestArchitecture once (then empty)."""

    def __init__(
        self, cached: TestArchitecture, arch: ArchitectureSpec,
    ) -> None:
        self._gate: PerArchOnce = PerArchOnce(cached, arch)

    def execute(self, context: TestArchitectureContext) -> TestArchitecture:
        return self._gate.take(context.module)


class CachedReviewSecurity:
    """Stand-in for ReviewSecurity that returns an empty SecurityReview."""

    def __init__(self, review: SecurityReview) -> None:
        self._review: SecurityReview = review

    def execute(self, context: SecurityReviewContext) -> SecurityReview:
        del context
        return self._review


class CachedGenerateSecurityTests:
    """Returns the cached merged security TestArchitecture once."""

    def __init__(
        self, cached: TestArchitecture, arch: ArchitectureSpec,
    ) -> None:
        self._gate: PerArchOnce = PerArchOnce(cached, arch)

    def execute(self, context: SecurityTestContext) -> TestArchitecture:
        return self._gate.take(context.module)


class CachedOrchestrateModule:
    """Stand-in for OrchestrateModule; returns cached ModuleImplementation."""

    def __init__(self, by_name: dict[str, ModuleImplementation]) -> None:
        self._by_name: dict[str, ModuleImplementation] = by_name

    def stamp_architecture(self, arch: ArchitectureSpec | None) -> None:
        del arch

    def execute(self, module: ModuleSpec) -> ModuleImplementation:
        return self._by_name[module.name]
