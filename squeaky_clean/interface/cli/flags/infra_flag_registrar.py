"""InfraFlagRegistrar: infrastructure, techspec, and wiring argparse flags."""

import argparse


class InfraFlagRegistrar:
    """Registers --infra mode, techspec inference/TTL, and wiring toggles."""

    def register(self, parser: argparse.ArgumentParser) -> None:
        """Add the infra + techspec flag block to ``parser``."""
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
