"""RunSettings: the run-config-relevant CLI knobs, decoupled from CLIArgs (R6.5)."""

from dataclasses import dataclass, field

from squeaky_clean.application.shared.gateways.cost_budget import CostBudget
from squeaky_clean.application.shared.gateways.prompt_cache_config import PromptCacheConfig
from squeaky_clean.application.shared.gateways.retry_policy import RetryPolicy
from squeaky_clean.interface.cli.invocations.infra_settings import InfraSettings


@dataclass(frozen=True)
class RunSettings:
    """Everything RunConfigFactory needs to assemble a RunConfig.

    Defaults mirror the CLI flag defaults. Retry/budget/cache arrive as the
    application-layer value objects (built once by CLIInvocationMapper) so no
    consumer ever re-reads raw flag fields off a wide bundle.
    """

    seed: int = 0
    temperature_architect: float | None = None
    temperature_icp: float | None = None
    deterministic: bool = False
    retry: RetryPolicy = field(default_factory=RetryPolicy)
    budget: CostBudget = field(default_factory=CostBudget)
    cache: PromptCacheConfig = field(default_factory=PromptCacheConfig)
    infra: InfraSettings = field(default_factory=InfraSettings)
    enable_sast: bool = False
    enable_security_tests: bool = False
    replay_only: bool = False
    architect_mode: str = "patterned"
