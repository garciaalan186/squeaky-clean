"""ResumeStubFactory: build a RunEvalDependencies that short-circuits cached stages."""

from __future__ import annotations

from dataclasses import replace
from typing import cast

from squeaky_clean.application.evaluation.eval.resume.resume_stubs import (
    CachedDesignArchitecture,
    CachedGenerateSecurityTests,
    CachedGenerateTestArchitecture,
    CachedOrchestrateModule,
    CachedReviewSecurity,
)
from squeaky_clean.application.evaluation.eval.run.run_eval_dependencies import RunEvalDependencies
from squeaky_clean.application.generation.architecture.design_architecture import DesignArchitecture
from squeaky_clean.application.generation.emission.module_implementation import ModuleImplementation
from squeaky_clean.application.generation.emission.orchestrate_module import OrchestrateModule
from squeaky_clean.application.generation.security.generate_security_tests import (
    GenerateSecurityTests,
)
from squeaky_clean.application.generation.security.review_security import ReviewSecurity
from squeaky_clean.application.generation.security.security_review import SecurityReview
from squeaky_clean.application.generation.testgen.generate_test_architecture import (
    GenerateTestArchitecture,
)
from squeaky_clean.application.generation.testgen.test_architecture import TestArchitecture
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec

_EMPTY = TestArchitecture(gherkin_scenarios=(), test_skeletons=())


class ResumeStubFactory:
    """Builder for one resumed run's RunEvalDependencies override bundle."""

    def __init__(self, deps: RunEvalDependencies, arch: ArchitectureSpec) -> None:
        self._deps: RunEvalDependencies = deps
        self._arch: ArchitectureSpec = arch
        self._test_arch: TestArchitecture = _EMPTY
        self._sec_arch: TestArchitecture = _EMPTY
        self._impls: tuple[ModuleImplementation, ...] = ()

    def with_test_archs(
        self, test_arch: TestArchitecture, sec_arch: TestArchitecture,
    ) -> ResumeStubFactory:
        self._test_arch, self._sec_arch = test_arch, sec_arch
        return self

    def with_impls(self, impls: tuple[ModuleImplementation, ...]) -> ResumeStubFactory:
        self._impls = impls
        return self

    def build(self, prior_cost_usd: float) -> RunEvalDependencies:
        """Return new deps with cached-stage stubs; seed the CostGate with the
        pre-checkpoint spend so a resumed run's budget is not reset to $0 (R0.5)."""
        if self._deps.cost_gate is not None:
            self._deps.cost_gate.seed(prior_cost_usd)
        impls_by_name = {i.module.name: i for i in self._impls}
        return replace(
            self._deps,
            design_architecture=cast(
                DesignArchitecture, CachedDesignArchitecture(self._arch),
            ),
            generate_test_architecture=cast(
                GenerateTestArchitecture,
                CachedGenerateTestArchitecture(self._test_arch, self._arch),
            ),
            review_security=cast(
                ReviewSecurity,
                CachedReviewSecurity(SecurityReview(concerns=())),
            ),
            generate_security_tests=cast(
                GenerateSecurityTests,
                CachedGenerateSecurityTests(self._sec_arch, self._arch),
            ),
            orchestrate_module=cast(
                OrchestrateModule, CachedOrchestrateModule(impls_by_name),
            ),
        )
