"""CLIArgs DTO: parsed command-line arguments for the Squeaky Clean CLI."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CLIArgs:
    """Immutable bundle of parsed CLI arguments.

    `problem_ids` lists which ProblemSpecs to run (1 in single mode,
    up to 16 in sweep mode). `max_parallel` caps concurrent problems.
    `model_override` forces all tiers to a single concrete model
    identifier when set — used for cost control during smoke tests.
    `seed` / `temperature_*` / `deterministic` control sampling for
    A4 reproducibility — see TemperaturePolicy.
    """

    problem_ids: tuple[str, ...]
    model_override: str | None
    max_parallel: int = 1
    replicates: int = 1
    problem_file: str | None = None
    seed: int = 0
    temperature_architect: float | None = None
    temperature_icp: float | None = None
    deterministic: bool = False
    max_icp_retries: int = 1
    max_fixer_passes: int = 1
    retry_backoff_base: float = 1.0
    max_cost_usd: float | None = None
    warn_cost_pct: float = 0.8
    enable_sast: bool = False
    prompt_cache: bool = True
    prompt_cache_tiers: tuple[str, ...] = (
        "architect", "manager", "icp", "fixer",
    )
    rebuild_dashboard: bool = False
    resume_run_dir: str | None = None
    infrastructure_mode: str = "manual"
    infer_infrastructure: bool = False
    techspec_cache_ttl_days: int = 30
    emit_wiring: bool = True
