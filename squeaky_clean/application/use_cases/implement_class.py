"""ImplementClass: ICP LLM call producing one ImplementedClass."""

from squeaky_clean.application.dtos.class_assignment import ClassAssignment
from squeaky_clean.application.dtos.implemented_class import ImplementedClass
from squeaky_clean.application.use_cases.class_assignment_formatter import (
    ClassAssignmentFormatter,
)
from squeaky_clean.application.use_cases.icp_execution_deps import IcpExecutionDeps
from squeaky_clean.application.use_cases.icp_retry_handler import ICPRetryHandler
from squeaky_clean.application.use_cases.load_agent_spec import LoadAgentSpec
from squeaky_clean.application.use_cases.parse_implemented_class import ParseImplementedClass
from squeaky_clean.application.use_cases.run_config import RunConfig
from squeaky_clean.application.use_cases.techspec_composer import TechSpecComposer
from squeaky_clean.domain.interfaces.llm_gateway import LLMGateway
from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.domain.interfaces.llm_response import LLMResponse
from squeaky_clean.domain.value_objects.model_tier import ModelTier
from squeaky_clean.infrastructure.llm.model_router import ModelRouter


class ImplementClass:
    """Runs an ICP call and retries up to ``RetryPolicy.max_icp_retries``."""

    def __init__(
        self, gateway: LLMGateway, router: ModelRouter,
        run_config: RunConfig | None = None,
        composer: TechSpecComposer | None = None,
        parser: ParseImplementedClass | None = None,
    ) -> None:
        rc = run_config or RunConfig()
        self._deps = IcpExecutionDeps(gateway=gateway, router=router, run_config=rc)
        self._loader = LoadAgentSpec()
        self._parser = parser or ParseImplementedClass()
        self._retry = ICPRetryHandler(gateway, rc.retry_policy, self._parser)
        self.composer: TechSpecComposer | None = composer
        self._composer: TechSpecComposer | None = composer

    def execute(self, assignment: ClassAssignment) -> ImplementedClass:
        """Generate code with bounded retry, then build the result."""
        request = self._make_request(assignment)
        first = self._deps.gateway.complete(request)
        response, retries = self._retry.run(
            request, assignment.class_spec.name, first,
        )
        return self._build(assignment, response, retries)

    def _build(
        self, assignment: ClassAssignment, response: LLMResponse, retries: int,
    ) -> ImplementedClass:
        class_name = assignment.class_spec.name
        code = self._parser.parse(response.content, class_name)
        return ImplementedClass(
            class_name=class_name,
            file_path=assignment.file_path,
            code=code, test_code=None,
            cost_usd=response.cost_usd,
            duration_ms=response.duration_ms,
            input_tokens=response.input_tokens,
            output_tokens=response.output_tokens,
            retries=retries,
        )

    def _make_request(self, assignment: ClassAssignment) -> LLMRequest:
        sampling = self._deps.run_config.sampling_for(ModelTier.ICP)
        if self._composer is not None and assignment.tech_spec is not None:
            prompt = self._composer.compose(assignment, assignment.tech_spec)
            sys_p, usr_p = prompt.system_prompt, prompt.user_prompt
        else:
            sys_p = self._loader.load(assignment.icp_spec_name)
            usr_p = ClassAssignmentFormatter(assignment.toolkit).format(assignment)
        return LLMRequest(
            model=self._deps.router.route(ModelTier.ICP),
            system_prompt=sys_p, user_prompt=usr_p,
            temperature=sampling.temperature, seed=sampling.seed,
            replicate_id=self._deps.run_config.replicate_id, tier="icp",
        )
