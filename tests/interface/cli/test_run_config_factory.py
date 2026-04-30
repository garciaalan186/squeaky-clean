"""Tests for RunConfigFactory."""

from squeaky_clean.domain.value_objects.model_tier import ModelTier
from squeaky_clean.interface.cli.cli_args import CLIArgs
from squeaky_clean.interface.cli.run_config_factory import RunConfigFactory


def _args(**overrides: object) -> CLIArgs:
    base: dict[str, object] = {
        "problem_ids": ("P0",), "model_override": None,
        "max_parallel": 1, "replicates": 1, "problem_file": None,
        "seed": 0, "temperature_architect": None,
        "temperature_icp": None, "deterministic": False,
        "max_icp_retries": 1, "max_fixer_passes": 1,
        "retry_backoff_base": 1.0, "max_cost_usd": None,
        "warn_cost_pct": 0.8,
    }
    base.update(overrides)
    return CLIArgs(**base)  # type: ignore[arg-type]


def test_default_args_yield_default_policy() -> None:
    rc = RunConfigFactory().build(_args())
    assert rc.sampling_for(ModelTier.ARCHITECT).temperature == 0.0
    assert rc.sampling_for(ModelTier.ICP).temperature == 0.2


def test_deterministic_flag_pins_all_tiers() -> None:
    rc = RunConfigFactory().build(_args(deterministic=True))
    assert rc.sampling_for(ModelTier.ICP).temperature == 0.0
    assert rc.sampling_for(ModelTier.ICP).seed == 0


def test_seed_flag_overrides_icp_seed() -> None:
    rc = RunConfigFactory().build(_args(seed=7))
    assert rc.sampling_for(ModelTier.ICP).seed == 7


def test_temperature_overrides_apply() -> None:
    rc = RunConfigFactory().build(_args(
        temperature_architect=0.3, temperature_icp=0.9,
    ))
    assert rc.sampling_for(ModelTier.ARCHITECT).temperature == 0.3
    assert rc.sampling_for(ModelTier.MANAGER).temperature == 0.3
    assert rc.sampling_for(ModelTier.ICP).temperature == 0.9


def test_retry_and_budget_flow_into_run_config() -> None:
    rc = RunConfigFactory().build(_args(
        max_icp_retries=3, max_fixer_passes=2, retry_backoff_base=0.25,
        max_cost_usd=4.5, warn_cost_pct=0.5,
    ))
    assert rc.retry_policy.max_icp_retries == 3
    assert rc.retry_policy.max_fixer_passes == 2
    assert rc.retry_policy.backoff_base_seconds == 0.25
    assert rc.cost_budget.max_cost_usd == 4.5
    assert rc.cost_budget.warn_at_pct == 0.5


def test_deterministic_preserves_retry_and_budget() -> None:
    rc = RunConfigFactory().build(_args(
        deterministic=True, max_icp_retries=2, max_cost_usd=1.0,
    ))
    assert rc.retry_policy.max_icp_retries == 2
    assert rc.cost_budget.max_cost_usd == 1.0
