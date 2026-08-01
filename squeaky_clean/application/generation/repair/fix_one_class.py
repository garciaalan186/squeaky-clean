"""FixOneClass: single Sonnet LLM call to repair one failing ImplementedClass."""

from squeaky_clean.application.generation.emission.dispatch.icp_execution_deps import (
    IcpExecutionDeps,
)
from squeaky_clean.application.generation.emission.implemented_class import ImplementedClass
from squeaky_clean.application.generation.emission.parsers.implemented_class_parse_error import (
    ImplementedClassParseError,
)
from squeaky_clean.application.generation.emission.parsers.parse_implemented_class import (
    ParseImplementedClass,
)
from squeaky_clean.application.generation.repair.fix_candidate import FixCandidate
from squeaky_clean.application.generation.repair.fix_prompt_builder import FixPromptBuilder
from squeaky_clean.application.shared.config.run_config import RunConfig
from squeaky_clean.domain.interfaces.llm_gateway import LLMGateway
from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.domain.interfaces.llm_response import LLMResponse
from squeaky_clean.domain.interfaces.model_routing_policy import ModelRoutingPolicy
from squeaky_clean.domain.value_objects.model_tier import ModelTier


class FixOneClass:
    """Runs a single fixer LLM call against a FixCandidate."""

    def __init__(
        self, gateway: LLMGateway, router: ModelRoutingPolicy,
        run_config: RunConfig | None = None,
    ) -> None:
        self._deps = IcpExecutionDeps(
            gateway=gateway, router=router,
            run_config=run_config or RunConfig())  # pure default (frozen config VO)
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
