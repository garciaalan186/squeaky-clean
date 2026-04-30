"""SecurityICPDispatcher: run Security ICPs in parallel for each concern."""

from concurrent.futures import ThreadPoolExecutor

from squeaky_clean.application.dtos.security_dispatch_context import SecurityDispatchContext
from squeaky_clean.application.dtos.test_architecture import TestArchitecture
from squeaky_clean.application.use_cases.load_agent_spec import LoadAgentSpec
from squeaky_clean.application.use_cases.map_concern_to_security_icp import (
    MapConcernToSecurityICP,
)
from squeaky_clean.application.use_cases.run_config import RunConfig
from squeaky_clean.application.use_cases.security_concern_formatter import (
    SecurityConcernFormatter,
)
from squeaky_clean.application.use_cases.security_test_assembler import SecurityTestAssembler
from squeaky_clean.domain.entities.class_spec import ClassSpec
from squeaky_clean.domain.interfaces.llm_gateway import LLMGateway
from squeaky_clean.domain.interfaces.llm_request import LLMRequest
from squeaky_clean.domain.interfaces.llm_response import LLMResponse
from squeaky_clean.domain.value_objects.model_tier import ModelTier
from squeaky_clean.infrastructure.llm.model_router import ModelRouter

_MAX_WORKERS: int = 4


class SecurityICPDispatcher:
    """Dispatches Security ICP calls in parallel and assembles results."""

    def __init__(
        self, gateway: LLMGateway, router: ModelRouter,
        run_config: RunConfig | None = None,
    ) -> None:
        self._gateway: LLMGateway = gateway
        self._router: ModelRouter = router
        self._run_config: RunConfig = run_config or RunConfig()
        self._loader: LoadAgentSpec = LoadAgentSpec()
        self._mapper: MapConcernToSecurityICP = MapConcernToSecurityICP()
        self._asm: SecurityTestAssembler = SecurityTestAssembler()

    def dispatch(self, ctx: SecurityDispatchContext) -> TestArchitecture:
        """Run all Security ICP calls in parallel, return assembled tests."""
        if not ctx.review.concerns:
            return TestArchitecture(gherkin_scenarios=(), test_skeletons=())
        class_map = {c.name: c for c in ctx.module.classes}
        self._fmt = SecurityConcernFormatter(
            toolkit=ctx.toolkit, module=ctx.module,
            architecture=ctx.architecture,
        )
        requests = self._build_requests(ctx, class_map)
        responses = self._run_parallel(requests)
        return self._asm.assemble(
            responses, ctx.review.concerns, class_map,
            module=ctx.module, toolkit=ctx.toolkit,
        )

    def _build_requests(
        self, ctx: SecurityDispatchContext, class_map: dict[str, ClassSpec],
    ) -> tuple[LLMRequest, ...]:
        model = self._router.route(ModelTier.ICP)
        sampling = self._run_config.sampling_for(ModelTier.ICP)
        result: list[LLMRequest] = []
        for concern in ctx.review.concerns:
            cls = class_map.get(concern.target_class)
            if cls is None:
                continue
            spec = self._mapper.map(concern.category, ctx.toolkit)
            result.append(LLMRequest(
                model=model,
                system_prompt=self._loader.load(spec),
                user_prompt=self._fmt.format(concern, cls),
                temperature=sampling.temperature, seed=sampling.seed,
                replicate_id=self._run_config.replicate_id,
                tier="icp",
            ))
        return tuple(result)

    def _run_parallel(
        self, requests: tuple[LLMRequest, ...],
    ) -> tuple[LLMResponse, ...]:
        if not requests:
            return ()
        with ThreadPoolExecutor(max_workers=_MAX_WORKERS) as pool:
            results = list(pool.map(self._gateway.complete, requests))
        return tuple(results)
