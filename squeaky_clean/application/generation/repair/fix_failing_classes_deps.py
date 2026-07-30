"""FixFailingClassesDeps: collaborators for the FixFailingClasses use case."""

from dataclasses import dataclass, field

from squeaky_clean.application.shared.config.run_config import RunConfig
from squeaky_clean.application.shared.gateways.llm_usage_recorder import LLMUsageRecorder
from squeaky_clean.application.shared.language.language_toolkit import LanguageToolkit
from squeaky_clean.domain.interfaces.llm_gateway import LLMGateway
from squeaky_clean.domain.interfaces.model_routing_policy import ModelRoutingPolicy


@dataclass(frozen=True)
class FixFailingClassesDeps:
    """Immutable bundle of collaborators FixFailingClasses needs.

    Bundling keeps the FixFailingClasses constructor within the
    <=2-args rule. The CLI composition root wires these in for one
    pipeline run, scoped to the current target language.
    """

    gateway: LLMGateway
    router: ModelRoutingPolicy
    recorder: LLMUsageRecorder
    toolkit: LanguageToolkit
    run_config: RunConfig = field(default_factory=RunConfig)
