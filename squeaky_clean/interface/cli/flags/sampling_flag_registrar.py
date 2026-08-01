"""SamplingFlagRegistrar: sampling, retry, and budget argparse flags."""

import argparse


class SamplingFlagRegistrar:
    """Registers seed/temperature/determinism, retry, and cost-cap flags."""

    def register(self, parser: argparse.ArgumentParser) -> None:
        """Add the sampling + budget flag block to ``parser``."""
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
