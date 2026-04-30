"""ResumeStubFactory: build a RunEvalDependencies that short-circuits cached stages."""

from __future__ import annotations

from dataclasses import replace
from typing import cast

from squeaky_clean.application.dtos.module_implementation import ModuleImplementation
from squeaky_clean.application.dtos.security_review import SecurityReview
from squeaky_clean.application.dtos.test_architecture import TestArchitecture
from squeaky_clean.application.use_cases.design_architecture import DesignArchitecture
from squeaky_clean.application.use_cases.generate_security_tests import (
    GenerateSecurityTests,
)
from squeaky_clean.application.use_cases.generate_test_architecture import (
    GenerateTestArchitecture,
)
from squeaky_clean.application.use_cases.orchestrate_module import OrchestrateModule
from squeaky_clean.application.use_cases.resume_stubs import (
    CachedDesignArchitecture,
    CachedGenerateSecurityTests,
    CachedGenerateTestArchitecture,
    CachedOrchestrateModule,
    CachedReviewSecurity,
)
from squeaky_clean.application.use_cases.review_security import ReviewSecurity
from squeaky_clean.application.use_cases.run_eval_dependencies import RunEvalDependencies
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec


class ResumeStubFactory:
    """Construct a RunEvalDependencies override bundle for resumed runs."""

    def build(
        self, deps: RunEvalDependencies, arch: ArchitectureSpec,
        test_arch: TestArchitecture, sec_arch: TestArchitecture,
        impls: tuple[ModuleImplementation, ...],
        prior_cost_usd: float,
    ) -> RunEvalDependencies:
        """Return new deps where cached-stage components are replaced by stubs."""
        impls_by_name = {i.module.name: i for i in impls}
        return replace(
            deps,
            design_architecture=cast(
                DesignArchitecture, CachedDesignArchitecture(arch),
            ),
            generate_test_architecture=cast(
                GenerateTestArchitecture,
                CachedGenerateTestArchitecture(test_arch, arch),
            ),
            review_security=cast(
                ReviewSecurity,
                CachedReviewSecurity(SecurityReview(concerns=())),
            ),
            generate_security_tests=cast(
                GenerateSecurityTests,
                CachedGenerateSecurityTests(sec_arch, arch),
            ),
            orchestrate_module=cast(
                OrchestrateModule, CachedOrchestrateModule(impls_by_name),
            ),
        )
