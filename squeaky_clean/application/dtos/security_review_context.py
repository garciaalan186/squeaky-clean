"""SecurityReviewContext DTO: inputs bundled for ReviewSecurity."""

from dataclasses import dataclass

from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec


@dataclass(frozen=True)
class SecurityReviewContext:
    """Immutable bundle of the ModuleSpec + ProblemSpec for SecurityArchitect.

    Bundling both on one DTO lets ``ReviewSecurity.execute`` stay within
    the <=2-args rule while carrying the class inventory and acceptance
    criteria needed to identify security concerns.
    """

    module: ModuleSpec
    problem: ProblemSpec
