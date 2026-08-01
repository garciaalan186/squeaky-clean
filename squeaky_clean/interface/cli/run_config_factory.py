"""RunConfigFactory: build a RunConfig from RunSettings (R6.5)."""

from squeaky_clean.application.shared.config.run_config import RunConfig
from squeaky_clean.domain.value_objects.model_tier import ModelTier
from squeaky_clean.domain.value_objects.temperature_policy import (
    TemperaturePolicy,
    TierSampling,
)
from squeaky_clean.interface.cli.invocations.run_settings import RunSettings


class RunConfigFactory:
    """Translates RunSettings into a RunConfig honoring overrides + flags."""

    def build(self, settings: RunSettings, replicate_id: int = 0) -> RunConfig:
        """Return a RunConfig: deterministic mode wins; else apply overrides."""
        if settings.deterministic:
            base = RunConfig.deterministic(replicate_id=replicate_id)
            return self._assemble(settings, base)
        base = RunConfig(
            seed=settings.seed, replicate_id=replicate_id,
            policy=self._policy_with_overrides(settings),
        )
        return self._assemble(settings, base)

    def _assemble(self, settings: RunSettings, base: RunConfig) -> RunConfig:
        return RunConfig(
            seed=base.seed, replicate_id=base.replicate_id, policy=base.policy,
            retry_policy=settings.retry, cost_budget=settings.budget,
            enable_sast=settings.enable_sast, prompt_cache_config=settings.cache,
            infrastructure_mode=settings.infra.infrastructure_mode,
            infer_infrastructure=settings.infra.infer_infrastructure,
            techspec_cache_ttl_days=settings.infra.techspec_cache_ttl_days,
            emit_wiring=settings.infra.emit_wiring,
            enable_security_tests=settings.enable_security_tests,
            replay_only=settings.replay_only,
            architect_mode=settings.architect_mode,
        )

    def _policy_with_overrides(self, settings: RunSettings) -> TemperaturePolicy:
        base = TemperaturePolicy.default().settings
        merged: dict[ModelTier, TierSampling] = dict(base)
        if settings.temperature_architect is not None:
            for tier in (ModelTier.ARCHITECT, ModelTier.MANAGER):
                merged[tier] = TierSampling(
                    temperature=settings.temperature_architect,
                    seed=base[tier].seed,
                )
        if settings.temperature_icp is not None:
            merged[ModelTier.ICP] = TierSampling(
                temperature=settings.temperature_icp,
                seed=base[ModelTier.ICP].seed,
            )
        return TemperaturePolicy(settings=merged)
