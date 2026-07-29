"""GenerateTestArchitectureDeps DTO: bundled deps for GenerateTestArchitecture."""

from dataclasses import dataclass, field

from squeaky_clean.application.dtos.language_toolkit import LanguageToolkit
from squeaky_clean.application.use_cases.llm_usage_recorder import LLMUsageRecorder
from squeaky_clean.application.use_cases.run_config import RunConfig
from squeaky_clean.domain.interfaces.llm_gateway import LLMGateway
from squeaky_clean.domain.interfaces.model_routing_policy import ModelRoutingPolicy


@dataclass(frozen=True)
class GenerateTestArchitectureDeps:
    """Immutable bundle of collaborators for GenerateTestArchitecture.

    Bundling gateway + router + toolkit + recorder + run_config lets
    the constructor stay within the hard <=2-args rule while
    parameterising the TestArchitect spec path by the active
    LanguageToolkit, recording token usage, and threading sampling
    settings through the pipeline.
    """

    gateway: LLMGateway
    router: ModelRoutingPolicy
    toolkit: LanguageToolkit
    recorder: LLMUsageRecorder
    run_config: RunConfig = field(default_factory=RunConfig)
