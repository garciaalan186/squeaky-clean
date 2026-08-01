"""RunConfig DTO: per-run sampling configuration (seed + replicate id)."""

from dataclasses import dataclass, field

from squeaky_clean.application.shared.gateways.cost_budget import CostBudget
from squeaky_clean.application.shared.gateways.prompt_cache_config import PromptCacheConfig
from squeaky_clean.application.shared.gateways.retry_policy import RetryPolicy
from squeaky_clean.domain.value_objects.model_tier import ModelTier
from squeaky_clean.domain.value_objects.temperature_policy import (
    TemperaturePolicy,
    TierSampling,
)


@dataclass(frozen=True)
class RunConfig:
    """Per-run configuration: seed, replicate_id, sampling, retry, budget."""

    seed: int = 0
    replicate_id: int = 0
    policy: TemperaturePolicy = TemperaturePolicy.default()
    retry_policy: RetryPolicy = field(default_factory=RetryPolicy)
    cost_budget: CostBudget = field(default_factory=CostBudget)
    enable_sast: bool = False
    prompt_cache_config: PromptCacheConfig = field(
        default_factory=PromptCacheConfig
    )
    infrastructure_mode: str = "manual"
    infer_infrastructure: bool = False
    techspec_cache_ttl_days: int = 30
    emit_wiring: bool = True
    # Auto-generated security tests are unanchored to the spec and flaky;
    # off by default so the generated suite is the acceptance contract.
    enable_security_tests: bool = False
    # Opt-in Manager-tier per-layer Verifier pass (the *Verifier.md specs) on
    # top of the mechanical arch.validate()/DependencyRule checks; off by
    # default (extra cost, unproven gain — enable to A/B via the eval harness).
    verify_layers: bool = False
    # R5.7: serve everything from cache; a miss raises (CI replay gate).
    replay_only: bool = False
    # R6.9 ablation: "patterned" (default) or "free" (all SimpleClass).
    architect_mode: str = "patterned"

    def sampling_for(self, tier: ModelTier) -> TierSampling:
        """Return effective TierSampling for ``tier`` using this run's seed."""
        base = self.policy.for_tier(tier)
        if base.seed is None:
            return base
        if tier is ModelTier.ICP:
            return TierSampling(temperature=base.temperature, seed=self.seed)
        return base

    @classmethod
    def deterministic(cls, replicate_id: int = 0) -> "RunConfig":
        """All tiers temp=0, seed=0 — fully deterministic."""
        return cls(
            seed=0, replicate_id=replicate_id,
            policy=TemperaturePolicy.deterministic(),
        )
