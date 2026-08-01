"""resume_stubs is a re-export module: every cached stub stays importable."""

from squeaky_clean.application.evaluation.eval.resume import resume_stubs
from squeaky_clean.application.evaluation.eval.resume.cached_design_architecture import (
    CachedDesignArchitecture,
)
from squeaky_clean.application.evaluation.eval.resume.cached_generate_security_tests import (
    CachedGenerateSecurityTests,
)
from squeaky_clean.application.evaluation.eval.resume.cached_generate_test_architecture import (
    CachedGenerateTestArchitecture,
)
from squeaky_clean.application.evaluation.eval.resume.cached_orchestrate_module import (
    CachedOrchestrateModule,
)
from squeaky_clean.application.evaluation.eval.resume.cached_review_security import (
    CachedReviewSecurity,
)


def test_reexports_are_the_canonical_classes() -> None:
    assert resume_stubs.CachedDesignArchitecture is CachedDesignArchitecture
    assert resume_stubs.CachedGenerateTestArchitecture is CachedGenerateTestArchitecture
    assert resume_stubs.CachedReviewSecurity is CachedReviewSecurity
    assert resume_stubs.CachedGenerateSecurityTests is CachedGenerateSecurityTests
    assert resume_stubs.CachedOrchestrateModule is CachedOrchestrateModule
