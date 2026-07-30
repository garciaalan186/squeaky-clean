"""IcpExecutionDeps: bundled deps for ICP-tier LLM use cases."""

from dataclasses import dataclass, field

from squeaky_clean.application.shared.config.run_config import RunConfig
from squeaky_clean.domain.interfaces.llm_gateway import LLMGateway
from squeaky_clean.domain.interfaces.model_routing_policy import ModelRoutingPolicy


@dataclass(frozen=True)
class IcpExecutionDeps:
    """Immutable bundle of collaborators for ICP/Fixer-tier LLM calls.

    Bundles gateway + router + run_config so ICP/Fixer classes that
    already had `(gateway, router)` constructors stay within the
    <=2-args rule while gaining tier-aware sampling control.
    """

    gateway: LLMGateway
    router: ModelRoutingPolicy
    run_config: RunConfig = field(default_factory=RunConfig)
