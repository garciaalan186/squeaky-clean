"""CLIArgsAssembler: converts a parsed argparse Namespace into CLIArgs."""

import argparse

from squeaky_clean.interface.cli.cli_args import CLIArgs


def _opt_str(value: object | None) -> str | None:
    return None if value is None else str(value)


def _opt_float(value: float | str | None) -> float | None:
    return None if value is None else float(value)


def _csv(value: object) -> tuple[str, ...]:
    return tuple(item.strip() for item in str(value).split(",") if item.strip())


class CLIArgsAssembler:
    """Builds the CLIArgs landing DTO from a parsed Namespace."""

    def assemble(self, ns: argparse.Namespace, ids: tuple[str, ...]) -> CLIArgs:
        """Return CLIArgs for ``ns`` with ``ids`` as the resolved problem ids."""
        return CLIArgs(
            problem_ids=ids,
            model_override=_opt_str(ns.model_override),
            max_parallel=int(ns.max_parallel),
            replicates=int(ns.replicates),
            problem_file=_opt_str(ns.problem_file),
            seed=int(ns.seed),
            temperature_architect=_opt_float(ns.temperature_architect),
            temperature_icp=_opt_float(ns.temperature_icp),
            deterministic=bool(ns.deterministic),
            max_icp_retries=int(ns.max_icp_retries),
            max_fixer_passes=int(ns.max_fixer_passes),
            retry_backoff_base=float(ns.retry_backoff_base),
            max_cost_usd=_opt_float(ns.max_cost_usd),
            warn_cost_pct=float(ns.warn_cost_pct),
            enable_sast=bool(ns.enable_sast),
            enable_security_tests=bool(ns.enable_security_tests),
            prompt_cache=bool(ns.prompt_cache),
            prompt_cache_tiers=_csv(ns.prompt_cache_tiers),
            rebuild_dashboard=bool(ns.rebuild_dashboard),
            micro_evals=bool(ns.micro_evals),
            micro_patterns=_csv(ns.micro_patterns),
            micro_languages=_csv(ns.micro_languages),
            replay_only=bool(ns.replay_only),
            architect_mode=str(ns.architect_mode),
            resume_run_dir=_opt_str(ns.resume_run_dir),
            infrastructure_mode=str(ns.infra),
            infer_infrastructure=bool(ns.infer_infrastructure),
            techspec_cache_ttl_days=int(ns.techspec_cache_ttl_days),
            emit_wiring=bool(ns.emit_wiring),
            squib_file=_opt_str(ns.squib_file),
            legacy_tests=_opt_str(ns.legacy_tests),
            recover_from=_opt_str(ns.recover_from),
            recover_out=_opt_str(ns.recover_out),
            recover_language=str(ns.recover_language),
            criteria=_csv(ns.criteria) if ns.criteria is not None else (),
            triage=_opt_str(ns.triage),
            refactor=_opt_str(ns.refactor),
            plan=_opt_str(ns.plan),
            refactor_out=_opt_str(ns.refactor_out),
        )
