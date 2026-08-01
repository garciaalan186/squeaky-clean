"""WiringContext: per-run shared collaborators for dependency wiring."""

from dataclasses import dataclass

from squeaky_clean.application.generation.emission.load_agent_spec import LoadAgentSpec
from squeaky_clean.application.shared.config.run_config import RunConfig
from squeaky_clean.application.shared.gateways.cost_gate import CostGate
from squeaky_clean.application.shared.gateways.llm_call_deps import LLMCallDeps
from squeaky_clean.application.shared.gateways.llm_usage_recorder import LLMUsageRecorder
from squeaky_clean.domain.interfaces.llm_gateway import LLMGateway
from squeaky_clean.infrastructure.filesystem.local_file_system import LocalFileSystem
from squeaky_clean.infrastructure.llm.model_router import ModelRouter
from squeaky_clean.infrastructure.observability.json_logger import JSONLogger
from squeaky_clean.interface.cli.wiring.gateway_stack_factory import GatewayStackFactory


@dataclass(frozen=True)
class WiringContext:
    """The collaborators every wiring concern shares within one run."""

    run_config: RunConfig
    router: ModelRouter
    gateway: LLMGateway
    cost_gate: CostGate
    fs: LocalFileSystem
    logger: JSONLogger
    loader: LoadAgentSpec
    recorder: LLMUsageRecorder
    call_deps: LLMCallDeps

    @classmethod
    def create(cls, router: ModelRouter, run_config: RunConfig) -> "WiringContext":
        """Build the shared context (gateway stack + fs/logger/recorder)."""
        logger = JSONLogger()
        gateway, cost_gate = GatewayStackFactory(logger).build(run_config)
        recorder = LLMUsageRecorder()
        return cls(
            run_config=run_config,
            router=router,
            gateway=gateway,
            cost_gate=cost_gate,
            fs=LocalFileSystem(),
            logger=logger,
            loader=LoadAgentSpec(),
            recorder=recorder,
            call_deps=LLMCallDeps(
                gateway=gateway, router=router, recorder=recorder,
                run_config=run_config,
            ),
        )
