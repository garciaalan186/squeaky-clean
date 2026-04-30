"""TestArchitectureContext DTO: inputs bundled for GenerateTestArchitecture."""

from dataclasses import dataclass

from squeaky_clean.application.dtos.language_toolkit import LanguageToolkit
from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec


@dataclass(frozen=True)
class TestArchitectureContext:
    """Immutable bundle of the ModuleSpec + ProblemSpec passed to TestArchitect.

    Keeping both on a single DTO lets `GenerateTestArchitecture.execute`
    stay within the ≤2-args rule while still carrying the acceptance
    criteria (from ProblemSpec) and the class inventory (from ModuleSpec)
    needed to produce Gherkin scenarios and test skeletons. ``toolkit``
    is optional so legacy call sites still work; when absent the
    formatter falls back to flat-layout hints. ``architecture`` is
    optional for resolving cross-module sibling dotted paths.
    """

    module: ModuleSpec
    problem: ProblemSpec
    toolkit: LanguageToolkit | None = None
    architecture: ArchitectureSpec | None = None
