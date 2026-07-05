"""SuppliedArchitectureDesigner: short-circuit the architect with a Squib."""

from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.application.use_cases.design_architecture import DesignArchitecture
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec


class SuppliedArchitectureDesigner(DesignArchitecture):
    """A DesignArchitecture that returns a pre-approved spec — no LLM call.

    Stage 6 injects this in place of the real architect so the human-
    reviewed Squib IS the architecture that gets regenerated. ``execute``
    ignores the ProblemSpec and returns the signed-off ArchitectureSpec;
    ``last_raw_notation`` exposes the Squib text so the pipeline persists
    exactly what the human approved. Because it overrides the two members
    the pipeline touches, it needs none of the parent's LLM collaborators.
    """

    def __init__(self, spec: ArchitectureSpec, notation: str) -> None:
        self._supplied: ArchitectureSpec = spec
        self._last_raw_notation: str = notation
        self._last_architecture_spec: ArchitectureSpec = spec

    def execute(
        self, problem: ProblemSpec, prior_violations: tuple[str, ...] = (),
    ) -> ArchitectureSpec:
        """Return the pre-approved spec, ignoring the ProblemSpec."""
        return self._supplied
