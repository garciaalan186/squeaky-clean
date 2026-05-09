"""FixOneClass: single Sonnet LLM call to repair one failing ImplementedClass."""

from squeaky_clean.application.dtos.fix_candidate import FixCandidate
from squeaky_clean.application.dtos.implemented_class import ImplementedClass
from squeaky_clean.application.use_cases.fix_prompt_builder import FixPromptBuilder
from squeaky_clean.application.use_cases.icp_execution_deps import IcpExecutionDeps
from squeaky_clean.application.use_cases.implemented_class_parse_error import (
    ImplementedClassParseError,
)
from squeaky_clean.application.use_cases.parse_implemented_class import ParseImplementedClass
from squeaky_clean.application.use_cases.run_config import RunConfig
from squeaky_clean.domain.interfaces.llm_gateway import LLMGateway
from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.domain.interfaces.llm_response import LLMResponse
from squeaky_clean.domain.value_objects.model_tier import ModelTier
from squeaky_clean.infrastructure.llm.model_router import ModelRouter


class FixOneClass:
    """Runs a single fixer LLM call against a FixCandidate."""

    def __init__(
        self, gateway: LLMGateway, router: ModelRouter,
        run_config: RunConfig | None = None,
    ) -> None:
        self._deps = IcpExecutionDeps(
            gateway=gateway, router=router,
            run_config=run_config or RunConfig())
        self._builder = FixPromptBuilder()
        self._parser = ParseImplementedClass()

    def execute(self, candidate: FixCandidate) -> tuple[ImplementedClass, LLMResponse]:
        """Call the fixer LLM once; return (new ImplementedClass, raw response).

        On parse error, keeps the original code (no-op fix) but still
        reports the response so its usage is billed to the fixer label.
        """
        sampling = self._deps.run_config.sampling_for(ModelTier.FIXER)
        request = LLMRequest(
            model=self._deps.router.route(ModelTier.FIXER),
            system_prompt=self._builder.system_prompt(),
            user_prompt=self._builder.user_prompt(candidate),
            temperature=sampling.temperature, seed=sampling.seed,
            replicate_id=self._deps.run_config.replicate_id,
            tier="fixer",
        )
        response = self._deps.gateway.complete(request)
        return self._build(candidate, response), response

    def _build(
        self, candidate: FixCandidate, response: LLMResponse,
    ) -> ImplementedClass:
        original = candidate.original
        try:
            new_code = self._parser.parse(response.content, original.class_name)
        except ImplementedClassParseError:
            new_code = original.code
        return ImplementedClass(
            class_name=original.class_name,
            file_path=original.file_path,
            code=new_code, test_code=original.test_code,
            cost_usd=original.cost_usd + response.cost_usd,
            duration_ms=original.duration_ms + response.duration_ms,
            input_tokens=original.input_tokens + response.input_tokens,
            output_tokens=original.output_tokens + response.output_tokens,
            retries=original.retries,
        )
