"""Tests for RunConfigFactory (RunSettings-based since R6.5)."""

from squeaky_clean.application.shared.gateways.cost_budget import CostBudget
from squeaky_clean.application.shared.gateways.retry_policy import RetryPolicy
from squeaky_clean.domain.value_objects.model_tier import ModelTier
from squeaky_clean.interface.cli.invocations.infra_settings import InfraSettings
from squeaky_clean.interface.cli.invocations.run_settings import RunSettings
from squeaky_clean.interface.cli.run_config_factory import RunConfigFactory


def test_default_settings_yield_default_policy() -> None:
    rc = RunConfigFactory().build(RunSettings())
    assert rc.sampling_for(ModelTier.ARCHITECT).temperature == 0.0
    assert rc.sampling_for(ModelTier.ICP).temperature == 0.2


def test_deterministic_flag_pins_all_tiers() -> None:
    rc = RunConfigFactory().build(RunSettings(deterministic=True))
    assert rc.sampling_for(ModelTier.ICP).temperature == 0.0
    assert rc.sampling_for(ModelTier.ICP).seed == 0


def test_seed_flag_overrides_icp_seed() -> None:
    rc = RunConfigFactory().build(RunSettings(seed=7))
    assert rc.sampling_for(ModelTier.ICP).seed == 7


def test_temperature_overrides_apply() -> None:
    rc = RunConfigFactory().build(RunSettings(
        temperature_architect=0.3, temperature_icp=0.9,
    ))
    assert rc.sampling_for(ModelTier.ARCHITECT).temperature == 0.3
    assert rc.sampling_for(ModelTier.MANAGER).temperature == 0.3
    assert rc.sampling_for(ModelTier.ICP).temperature == 0.9


def test_retry_and_budget_flow_into_run_config() -> None:
    rc = RunConfigFactory().build(RunSettings(
        retry=RetryPolicy(
            max_icp_retries=3, max_fixer_passes=2, backoff_base_seconds=0.25,
        ),
        budget=CostBudget(max_cost_usd=4.5, warn_at_pct=0.5),
    ))
    assert rc.retry_policy.max_icp_retries == 3
    assert rc.retry_policy.max_fixer_passes == 2
    assert rc.retry_policy.backoff_base_seconds == 0.25
    assert rc.cost_budget.max_cost_usd == 4.5
    assert rc.cost_budget.warn_at_pct == 0.5


def test_deterministic_preserves_retry_and_budget() -> None:
    rc = RunConfigFactory().build(RunSettings(
        deterministic=True,
        retry=RetryPolicy(max_icp_retries=2),
        budget=CostBudget(max_cost_usd=1.0),
    ))
    assert rc.retry_policy.max_icp_retries == 2
    assert rc.cost_budget.max_cost_usd == 1.0


def test_infra_and_mode_flags_flow_into_run_config() -> None:
    rc = RunConfigFactory().build(RunSettings(
        infra=InfraSettings(
            infrastructure_mode="auto", infer_infrastructure=True,
            techspec_cache_ttl_days=7, emit_wiring=False,
        ),
        replay_only=True, architect_mode="free",
        enable_sast=True, enable_security_tests=True,
    ))
    assert rc.infrastructure_mode == "auto"
    assert rc.infer_infrastructure is True
    assert rc.techspec_cache_ttl_days == 7
    assert rc.emit_wiring is False
    assert rc.replay_only is True
    assert rc.architect_mode == "free"
    assert rc.enable_sast is True
    assert rc.enable_security_tests is True
