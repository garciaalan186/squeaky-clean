"""CLIInvocationMapper: the ONLY consumer of CLIArgs — splits it per command (R6.5)."""

from squeaky_clean.application.shared.gateways.cost_budget import CostBudget
from squeaky_clean.application.shared.gateways.prompt_cache_config import PromptCacheConfig
from squeaky_clean.application.shared.gateways.retry_policy import RetryPolicy
from squeaky_clean.interface.cli.cli_args import CLIArgs
from squeaky_clean.interface.cli.invocations.cli_request import CLIRequest
from squeaky_clean.interface.cli.invocations.infra_settings import InfraSettings
from squeaky_clean.interface.cli.invocations.maintenance_invocation import MaintenanceInvocation
from squeaky_clean.interface.cli.invocations.micro_eval_invocation import MicroEvalInvocation
from squeaky_clean.interface.cli.invocations.recovery_invocation import RecoveryInvocation
from squeaky_clean.interface.cli.invocations.run_invocation import RunInvocation
from squeaky_clean.interface.cli.invocations.run_settings import RunSettings


class CLIInvocationMapper:
    """Post-parse mapping layer: CLIArgs stays the argparse landing DTO only."""

    def map(self, args: CLIArgs) -> CLIRequest:
        """Derive the four per-command invocation configs from the flat namespace."""
        settings = self._settings(args)
        return CLIRequest(
            run=RunInvocation(
                problem_ids=args.problem_ids, problem_file=args.problem_file,
                replicates=args.replicates, max_parallel=args.max_parallel,
                model_override=args.model_override, settings=settings,
            ),
            recovery=RecoveryInvocation(
                squib_file=args.squib_file, legacy_tests=args.legacy_tests,
                recover_from=args.recover_from, recover_out=args.recover_out,
                recover_language=args.recover_language, criteria=args.criteria,
                triage=args.triage, refactor=args.refactor, plan=args.plan,
                refactor_out=args.refactor_out, settings=settings,
            ),
            micro_eval=MicroEvalInvocation(
                enabled=args.micro_evals, model_override=args.model_override,
                patterns=args.micro_patterns,
                languages=args.micro_languages, settings=settings,
            ),
            maintenance=MaintenanceInvocation(
                rebuild_dashboard=args.rebuild_dashboard,
                resume_run_dir=args.resume_run_dir,
                problem_ids=args.problem_ids, problem_file=args.problem_file,
                settings=settings,
            ),
        )

    def _settings(self, args: CLIArgs) -> RunSettings:
        return RunSettings(
            seed=args.seed,
            temperature_architect=args.temperature_architect,
            temperature_icp=args.temperature_icp,
            deterministic=args.deterministic,
            retry=RetryPolicy(
                max_icp_retries=args.max_icp_retries,
                max_fixer_passes=args.max_fixer_passes,
                backoff_base_seconds=args.retry_backoff_base,
            ),
            budget=CostBudget(
                max_cost_usd=args.max_cost_usd, warn_at_pct=args.warn_cost_pct,
            ),
            cache=PromptCacheConfig(
                enabled=args.prompt_cache, enabled_tiers=args.prompt_cache_tiers,
            ),
            infra=InfraSettings(
                infrastructure_mode=args.infrastructure_mode,
                infer_infrastructure=args.infer_infrastructure,
                techspec_cache_ttl_days=args.techspec_cache_ttl_days,
                emit_wiring=args.emit_wiring,
            ),
            enable_sast=args.enable_sast,
            enable_security_tests=args.enable_security_tests,
            replay_only=args.replay_only,
            architect_mode=args.architect_mode,
        )
