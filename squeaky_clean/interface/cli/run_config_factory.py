"""RunConfigFactory: build a RunConfig from CLIArgs."""

from squeaky_clean.application.dtos.cost_budget import CostBudget
from squeaky_clean.application.dtos.prompt_cache_config import PromptCacheConfig
from squeaky_clean.application.dtos.retry_policy import RetryPolicy
from squeaky_clean.application.use_cases.run_config import RunConfig
from squeaky_clean.domain.value_objects.model_tier import ModelTier
from squeaky_clean.infrastructure.llm.temperature_policy import (
    TemperaturePolicy,
    TierSampling,
)
from squeaky_clean.interface.cli.cli_args import CLIArgs


class RunConfigFactory:
    """Translates CLIArgs into a RunConfig honoring overrides + flags."""

    def build(self, args: CLIArgs, replicate_id: int = 0) -> RunConfig:
        """Return a RunConfig: deterministic mode wins; else apply overrides."""
        retry = RetryPolicy(
            max_icp_retries=args.max_icp_retries,
            max_fixer_passes=args.max_fixer_passes,
            backoff_base_seconds=args.retry_backoff_base,
        )
        budget = CostBudget(
            max_cost_usd=args.max_cost_usd, warn_at_pct=args.warn_cost_pct,
        )
        cache_cfg = PromptCacheConfig(
            enabled=args.prompt_cache,
            enabled_tiers=args.prompt_cache_tiers,
        )
        if args.deterministic:
            base = RunConfig.deterministic(replicate_id=replicate_id)
            return RunConfig(
                seed=base.seed, replicate_id=base.replicate_id,
                policy=base.policy, retry_policy=retry, cost_budget=budget,
                enable_sast=args.enable_sast, prompt_cache_config=cache_cfg,
                infrastructure_mode=args.infrastructure_mode,
                infer_infrastructure=args.infer_infrastructure,
                techspec_cache_ttl_days=args.techspec_cache_ttl_days,
                emit_wiring=args.emit_wiring,
            )
        policy = self._policy_with_overrides(args)
        return RunConfig(
            seed=args.seed, replicate_id=replicate_id, policy=policy,
            retry_policy=retry, cost_budget=budget,
            enable_sast=args.enable_sast, prompt_cache_config=cache_cfg,
            infrastructure_mode=args.infrastructure_mode,
            infer_infrastructure=args.infer_infrastructure,
            techspec_cache_ttl_days=args.techspec_cache_ttl_days,
            emit_wiring=args.emit_wiring,
        )

    def _policy_with_overrides(self, args: CLIArgs) -> TemperaturePolicy:
        base = TemperaturePolicy.default().settings
        merged: dict[ModelTier, TierSampling] = dict(base)
        if args.temperature_architect is not None:
            for tier in (ModelTier.ARCHITECT, ModelTier.MANAGER):
                merged[tier] = TierSampling(
                    temperature=args.temperature_architect,
                    seed=base[tier].seed,
                )
        if args.temperature_icp is not None:
            merged[ModelTier.ICP] = TierSampling(
                temperature=args.temperature_icp,
                seed=base[ModelTier.ICP].seed,
            )
        return TemperaturePolicy(settings=merged)
