"""SecurityTestContext DTO: inputs bundled for GenerateSecurityTests."""

from dataclasses import dataclass

from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.application.dtos.security_review import SecurityReview
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec


@dataclass(frozen=True)
class SecurityTestContext:
    """Immutable bundle of SecurityReview + ModuleSpec + ProblemSpec.

    Bundling on one DTO lets ``GenerateSecurityTests.execute``
    stay within the <=2-args rule while carrying the security concerns,
    class signatures, and problem context. ``architecture`` (optional)
    lets the formatter resolve cross-module dependency dotted paths.
    """

    review: SecurityReview
    module: ModuleSpec
    problem: ProblemSpec
    architecture: ArchitectureSpec | None = None
