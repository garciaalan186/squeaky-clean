"""CLIArgsParser: converts argv into a CLIArgs dataclass via argparse."""

import argparse

from squeaky_clean.interface.cli.cli_args import CLIArgs

_ALL_PROBLEMS: tuple[str, ...] = (
    "P0", "P0JS", "P0TS", "P0JAVA", "P0GO", "P0RUST",
    "P1", "P1JS", "P1TS", "P1JAVA",
    "P2", "P2JS", "P2TS", "P2JAVA",
    "P3", "P3JS", "P3TS", "P3JAVA",
    "P4", "P5",
)


class CLIArgsParser:
    """Parses a list of CLI arguments into a CLIArgs DTO."""

    def parse(self, argv: list[str]) -> CLIArgs:
        """Return a CLIArgs built from argparse over ``argv``."""
        parser = self._build()
        ns = parser.parse_args(argv)
        ids = self._resolve_ids(ns)
        if (not ids and not ns.problem_file and not ns.rebuild_dashboard
                and ns.resume_run_dir is None and ns.squib_file is None):
            parser.error(
                "one of --problem, --problems, --sweep, --problem-file, "
                "--squib-file, --rebuild-dashboard, or --resume required"
            )
        return CLIArgs(
            problem_ids=ids,
            model_override=(
                str(ns.model_override) if ns.model_override is not None else None
            ),
            max_parallel=int(ns.max_parallel),
            replicates=int(ns.replicates),
            problem_file=(
                str(ns.problem_file) if ns.problem_file is not None else None
            ),
            seed=int(ns.seed),
            temperature_architect=(
                float(ns.temperature_architect)
                if ns.temperature_architect is not None else None
            ),
            temperature_icp=(
                float(ns.temperature_icp)
                if ns.temperature_icp is not None else None
            ),
            deterministic=bool(ns.deterministic),
            max_icp_retries=int(ns.max_icp_retries),
            max_fixer_passes=int(ns.max_fixer_passes),
            retry_backoff_base=float(ns.retry_backoff_base),
            max_cost_usd=(
                float(ns.max_cost_usd) if ns.max_cost_usd is not None else None
            ),
            warn_cost_pct=float(ns.warn_cost_pct),
            enable_sast=bool(ns.enable_sast),
            prompt_cache=bool(ns.prompt_cache),
            prompt_cache_tiers=tuple(
                t.strip() for t in str(ns.prompt_cache_tiers).split(",") if t.strip()
            ),
            rebuild_dashboard=bool(ns.rebuild_dashboard),
            resume_run_dir=(
                str(ns.resume_run_dir) if ns.resume_run_dir is not None else None
            ),
            infrastructure_mode=str(ns.infra),
            infer_infrastructure=bool(ns.infer_infrastructure),
            techspec_cache_ttl_days=int(ns.techspec_cache_ttl_days),
            emit_wiring=bool(ns.emit_wiring),
            squib_file=(str(ns.squib_file) if ns.squib_file is not None else None),
            legacy_tests=(
                str(ns.legacy_tests) if ns.legacy_tests is not None else None
            ),
        )

    def _build(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            prog="squeaky",
            description="Squeaky Clean meta-recursive pipeline CLI",
        )
        group = parser.add_mutually_exclusive_group()
        group.add_argument("--problem", dest="problem_id", default=None,
                           help="Single problem id (e.g. P0)")
        group.add_argument("--problems", dest="problems_csv", default=None,
                           help="CSV list of problem ids (e.g. P0,P1JS)")
        group.add_argument("--sweep", dest="sweep", action="store_true",
                           help="Run all 16 problems in parallel")
        parser.add_argument("--model-override", dest="model_override",
                            default=None,
                            help="Force all tiers to one model identifier")
        parser.add_argument("--max-parallel", dest="max_parallel", type=int,
                            default=4,
                            help="Concurrent problems in sweep mode (default 4)")
        parser.add_argument("--replicates", dest="replicates", type=int,
                            default=1,
                            help="Number of replicate runs per problem (default 1)")
        parser.add_argument("--problem-file", dest="problem_file", default=None,
                            help="Path to a JSON ProblemSpec file")
        parser.add_argument("--seed", dest="seed", type=int, default=0,
                            help="Per-run seed for sampled (ICP) calls (default 0)")
        parser.add_argument("--temperature-architect",
                            dest="temperature_architect",
                            type=float, default=None,
                            help="Override temperature for architect/manager tiers")
        parser.add_argument("--temperature-icp", dest="temperature_icp",
                            type=float, default=None,
                            help="Override temperature for ICP tier (default 0.2)")
        parser.add_argument("--deterministic", dest="deterministic",
                            action="store_true",
                            help="Pin all tiers to temperature=0, seed=0")
        parser.add_argument("--max-icp-retries", dest="max_icp_retries",
                            type=int, default=1,
                            help="Max ICP retry attempts on parse failure")
        parser.add_argument("--max-fixer-passes", dest="max_fixer_passes",
                            type=int, default=1,
                            help="Max fixer-stage passes after a failing test run")
        parser.add_argument("--retry-backoff-base", dest="retry_backoff_base",
                            type=float, default=1.0,
                            help="Base seconds for exponential retry backoff")
        parser.add_argument("--max-cost-usd", dest="max_cost_usd",
                            type=float, default=None,
                            help="Hard USD cap; pipeline aborts gracefully if hit")
        parser.add_argument("--warn-cost-pct", dest="warn_cost_pct",
                            type=float, default=0.8,
                            help="Warn at this fraction of the cost cap (0,1]")
        parser.add_argument("--enable-sast", dest="enable_sast",
                            action="store_true",
                            help="Run bandit SAST over generated code (opt-in)")
        cache_group = parser.add_mutually_exclusive_group()
        cache_group.add_argument(
            "--prompt-cache", dest="prompt_cache", action="store_true",
            default=True,
            help="Attach Anthropic ephemeral cache_control (default on)",
        )
        cache_group.add_argument(
            "--no-prompt-cache", dest="prompt_cache", action="store_false",
            help="Disable Anthropic ephemeral cache_control globally",
        )
        parser.add_argument(
            "--prompt-cache-tiers", dest="prompt_cache_tiers",
            default="architect,manager,icp,fixer",
            help="CSV subset of tiers to cache (default: all four)",
        )
        parser.add_argument(
            "--rebuild-dashboard", dest="rebuild_dashboard",
            action="store_true",
            help="Rebuild meta-evaluation-results/dashboard.html and exit",
        )
        parser.add_argument(
            "--resume", dest="resume_run_dir", default=None,
            help="Resume a partially-completed run from this run dir",
        )
        parser.add_argument(
            "--infra", dest="infra",
            choices=["manual", "auto"], default="manual",
            help=(
                "Infrastructure adapter generation mode (H1 default: manual). "
                "auto engages the Tier C path for Infrastructure-layer "
                "Repository/Gateway/Adapter assignments."
            ),
        )
        parser.add_argument(
            "--infer-infrastructure", dest="infer_infrastructure",
            action="store_true", default=False,
            help=(
                "H3: enable MCDA-based InfrastructureChoiceArchitect to derive "
                "infrastructure choices not declared on the ProblemSpec. "
                "Default off; requires --infra=auto."
            ),
        )
        parser.add_argument(
            "--techspec-cache-ttl-days", dest="techspec_cache_ttl_days",
            type=int, default=30,
            help=(
                "H4: TTL in days for cached TechSpec entries (default 30). "
                "Stale-tolerant grace allows reuse for 1.5x TTL on outage."
            ),
        )
        wiring_group = parser.add_mutually_exclusive_group()
        wiring_group.add_argument(
            "--emit-wiring", dest="emit_wiring", action="store_true",
            default=True,
            help=(
                "Emit src/main.py composition root (default true when "
                "--infra=auto; ignored when --infra=manual)."
            ),
        )
        wiring_group.add_argument(
            "--no-emit-wiring", dest="emit_wiring", action="store_false",
            help="Disable WiringGenerator output for this run.",
        )
        parser.add_argument(
            "--squib-file", dest="squib_file", default=None,
            help="Regenerate from a signed-off recovery Squib, bypassing "
                 "the architect (Agentic Architecture Recovery, Stage 6).",
        )
        parser.add_argument(
            "--legacy-tests", dest="legacy_tests", default=None,
            help="Directory of the brownfield project's tests; acceptance "
                 "criteria are derived from its test_* functions.",
        )
        return parser

    def _resolve_ids(self, ns: argparse.Namespace) -> tuple[str, ...]:
        if ns.sweep:
            return _ALL_PROBLEMS
        if ns.problems_csv is not None:
            return tuple(p.strip() for p in str(ns.problems_csv).split(",") if p.strip())
        if ns.problem_id is not None:
            return (str(ns.problem_id),)
        return ()
