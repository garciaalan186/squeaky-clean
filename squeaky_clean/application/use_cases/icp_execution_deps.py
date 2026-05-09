"""IcpExecutionDeps: bundled deps for ICP-tier LLM use cases."""

from dataclasses import dataclass, field

from squeaky_clean.application.use_cases.run_config import RunConfig
from squeaky_clean.domain.interfaces.llm_gateway import LLMGateway
from squeaky_clean.infrastructure.llm.model_router import ModelRouter


@dataclass(frozen=True)
class IcpExecutionDeps:
    """Immutable bundle of collaborators for ICP/Fixer-tier LLM calls.

    Bundles gateway + router + run_config so ICP/Fixer classes that
    already had `(gateway, router)` constructors stay within the
    <=2-args rule while gaining tier-aware sampling control.
    """

    gateway: LLMGateway
    router: ModelRouter
    run_config: RunConfig = field(default_factory=RunConfig)
