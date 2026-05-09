"""LLMCallDeps DTO: bundled deps for architect-tier LLM use cases."""

from dataclasses import dataclass, field

from squeaky_clean.application.use_cases.llm_usage_recorder import LLMUsageRecorder
from squeaky_clean.application.use_cases.run_config import RunConfig
from squeaky_clean.domain.interfaces.llm_gateway import LLMGateway
from squeaky_clean.infrastructure.llm.model_router import ModelRouter


@dataclass(frozen=True)
class LLMCallDeps:
    """Immutable bundle of collaborators for an architect-tier LLM call.

    Bundling gateway + router + recorder + run_config onto one DTO lets
    the use-case constructors stay within the hard <=2-args rule while
    still threading shared collaborators through the pipeline.
    """

    gateway: LLMGateway
    router: ModelRouter
    recorder: LLMUsageRecorder
    run_config: RunConfig = field(default_factory=RunConfig)
