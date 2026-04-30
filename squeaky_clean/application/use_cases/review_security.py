"""ReviewSecurity: ask the SecurityArchitect LLM to review a ModuleSpec."""

from squeaky_clean.application.dtos.security_review import SecurityReview
from squeaky_clean.application.dtos.security_review_context import SecurityReviewContext
from squeaky_clean.application.use_cases.llm_call_deps import LLMCallDeps
from squeaky_clean.application.use_cases.load_agent_spec import LoadAgentSpec
from squeaky_clean.application.use_cases.parse_security_review import ParseSecurityReview
from squeaky_clean.application.use_cases.security_review_formatter import (
    SecurityReviewFormatter,
)
from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.domain.value_objects.model_tier import ModelTier

_SPEC_NAME: str = "SecurityArchitect"


class ReviewSecurity:
    """Use case: produce a SecurityReview from a ModuleSpec + ProblemSpec via LLM."""

    def __init__(self, deps: LLMCallDeps) -> None:
        self._deps: LLMCallDeps = deps
        self._loader: LoadAgentSpec = LoadAgentSpec()
        self._parser: ParseSecurityReview = ParseSecurityReview()
        self._formatter: SecurityReviewFormatter = SecurityReviewFormatter()

    def execute(self, context: SecurityReviewContext) -> SecurityReview:
        """Run the SecurityArchitect and return its parsed SecurityReview."""
        system_prompt = self._loader.load(_SPEC_NAME)
        user_prompt = self._formatter.format(context)
        sampling = self._deps.run_config.sampling_for(ModelTier.MANAGER)
        request = LLMRequest(
            model=self._deps.router.route(ModelTier.MANAGER),
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            temperature=sampling.temperature, seed=sampling.seed,
            replicate_id=self._deps.run_config.replicate_id,
            tier="manager",
        )
        response = self._deps.gateway.complete(request)
        self._deps.recorder.record(response, "security_architect")
        return self._parser.parse(response.content)
