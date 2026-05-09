"""DesignArchitecture: ask PrincipalArchitect for a (multi-module) ArchitectureSpec.

`execute()` returns the full `ArchitectureSpec`. For legacy callers that
need just one module, `execute_first_module()` is provided.
"""

from squeaky_clean.application.dtos.problem_spec import ProblemSpec
from squeaky_clean.application.use_cases.design_architecture_error import (
    DesignArchitectureError,
)
from squeaky_clean.application.use_cases.llm_call_deps import LLMCallDeps
from squeaky_clean.application.use_cases.load_agent_spec import LoadAgentSpec
from squeaky_clean.application.use_cases.parse_architecture_notation import (
    ParseArchitectureNotation,
)
from squeaky_clean.application.use_cases.problem_spec_formatter import ProblemSpecFormatter
from squeaky_clean.domain.entities.architecture_spec import ArchitectureSpec
from squeaky_clean.domain.entities.module_spec import ModuleSpec
from squeaky_clean.domain.entities.notation_parse_error import NotationParseError
from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.domain.value_objects.model_tier import ModelTier

_ARCHITECT_SPEC: str = "PrincipalArchitect"


class DesignArchitecture:
    """Use case: produce a validated ArchitectureSpec from a ProblemSpec."""

    def __init__(self, deps: LLMCallDeps) -> None:
        self._deps: LLMCallDeps = deps
        self._loader: LoadAgentSpec = LoadAgentSpec()
        self._parser: ParseArchitectureNotation = ParseArchitectureNotation()
        self._formatter: ProblemSpecFormatter = ProblemSpecFormatter()

    def execute(
        self, problem: ProblemSpec,
        prior_violations: tuple[str, ...] = (),
    ) -> ArchitectureSpec:
        """Run PA; retry once on parse error; return ArchitectureSpec.

        ``prior_violations`` re-invokes after a downstream validator
        (e.g. constraint #22) rejected the previous output.
        """
        system = self._loader.load(_ARCHITECT_SPEC)
        user = self._formatter.format(problem)
        if prior_violations:
            user = (f"{user}\n\nYour prior output had these constraint #22 "
                    f"violations: {list(prior_violations)}. "
                    f"Re-emit, fixing them.")
        try:
            return self._call(system, user)
        except DesignArchitectureError as first_err:
            return self._call(system, f"{user}\n\nRETRY: previous attempt "
                              f"failed: {first_err}\nFix and emit valid §Notation.")

    def execute_first_module(self, problem: ProblemSpec) -> ModuleSpec:
        """Backward-compat helper: returns just the first ModuleSpec."""
        return self.execute(problem).modules[0]

    def _call(self, system: str, user: str) -> ArchitectureSpec:
        sampling = self._deps.run_config.sampling_for(ModelTier.ARCHITECT)
        request = LLMRequest(
            model=self._deps.router.route(ModelTier.ARCHITECT),
            system_prompt=system, user_prompt=user,
            temperature=sampling.temperature, seed=sampling.seed,
            replicate_id=self._deps.run_config.replicate_id,
            tier="architect",
        )
        response = self._deps.gateway.complete(request)
        self._deps.recorder.record(response, "architect")
        self._last_raw_notation = response.content
        try:
            arch = self._parser.parse(response.content)
        except NotationParseError as exc:
            raise DesignArchitectureError(
                f"unparseable §Notation: {exc}"
            ) from exc
        violations = arch.validate()
        if violations:
            raise DesignArchitectureError(
                "invalid ArchitectureSpec: " + "; ".join(violations)
            )
        self._last_architecture_spec = arch
        return arch

    @property
    def last_raw_notation(self) -> str:
        """Return raw §Notation from the most recent call."""
        return getattr(self, "_last_raw_notation", "")

    @property
    def last_architecture_spec(self) -> ArchitectureSpec | None:
        """Return the full ArchitectureSpec from the most recent call."""
        return getattr(self, "_last_architecture_spec", None)
